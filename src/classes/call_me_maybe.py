#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   call_me_maybe.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:20:32 by varandri            #+#    #+#            #
#   Updated: 2026/10/14 14:46:31 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Select functions and generate their arguments with a language model."""

try:
    from typing import Any
    from .enums import States, Types
    from pydantic import BaseModel, Field, ConfigDict
    from .models import FunctionCalling, FunctionDefinition, TransitionState
    from .llm_wrapper import Llm
    from json import dumps, loads, JSONDecodeError
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


class CallMeMaybe(BaseModel):
    """Coordinate function selection and argument generation.

    Attributes:
        func_defs: Function definitions available for selection.
        func_calls: Prompts to resolve into function calls.
        model: Language model used to generate function names and arguments.
        transition_state: Current function-selection or parameter state.
    """

    func_defs: list[FunctionDefinition] = Field(default=...)
    func_calls: list[FunctionCalling] = Field(default=...)
    model: Llm = Field(default=Llm())
    transition_state: TransitionState = Field(default=TransitionState())
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __set_state(
        self, state: States = States.NAME,
        param_keys: tuple[str, Types] | None = None
    ) -> None:
        """Set the current generation state and optional parameter key.

        Args:
            state: Generation stage to activate.
            param_keys: Parameter name and type to track, if applicable.
        """
        transition_state: TransitionState = self.transition_state
        transition_state.state = state
        transition_state.parameter_key = param_keys

    def __get_prompt(
        self, call: str, func_defs: list[dict[str, Any]] = [],
        func_name: str = ""
    ) -> str:
        """Build a prompt for selecting a function or retrieving arguments.

        Args:
            call: User prompt describing the requested function call.
            func_defs: Function definitions available for selection.
            func_name: Selected function whose arguments are being retrieved.

        Returns:
            The prompt text sent to the language model.
        """
        from ..functions import get_function_struct
        transition_state: TransitionState = self.transition_state
        if transition_state.state == States.NAME:
            return (
                "You are a function selector.\n"
                "You will select a function_name from "
                "a list of given function definitions.\n"
                "You will chose the function that match the one "
                "described in a given prompt.\n"
                'the format is as: "name": "fn_function_name".\n'
                f"Function Definitions: {func_defs}. Output:"
                '{'f'"prompt":"{call}", "name": '
            )
        func_struct = get_function_struct(
            func_name=func_name, func_defs=self.func_defs
        )
        return (
            "You are a parameter retriever.\n"
            "You will retrieve the parameters value of a function "
            "in a given prompt. The function structure will also "
            "be given to you for you to take reference on.\n"
            "the value must be a valid JSON value."
            "For a numeric value ,number starting with 0, 0 is skipped.\n"
            "Example: 02 is 2 002 is 2 , 09 is 9 and so on.\n"
            f"Function structure: {func_struct}.\n"
            "{"
            f'"prompt": {dumps(call)}, "name": '
            f'"{func_name}", "parameters":'
        )

    def __call_name(
        self, call: str, func_defs: list[dict[str, Any]],
        func_names: list[str]
    ) -> str:
        """Generate the function name selected for a prompt.

        Args:
            call: User prompt describing the requested function call.
            func_defs: Function definitions supplied to the model.
            func_names: Valid function names used to constrain selection.

        Returns:
            The selected function name encoded as a JSON string.
        """
        from ..functions import get_options
        self.__set_state()
        print(f'Prompt: {dumps(call)}')
        print("Function Name: ", end="", flush=True)
        model: Llm = self.model
        func_name = ""
        max_token = 20
        prompt = self.__get_prompt(call, func_defs)
        encoded_prompt = model.encode_to_int(prompt)
        while True:
            name_options = get_options(caller=self, found_name=func_name)
            if (
                max_token <= 0 or
                func_name in func_names
            ):
                break
            best_token = model.get_best_token(
                prompt=encoded_prompt, options=name_options
            )
            decoded_token = model.decode([best_token])
            max_token -= 1
            print(f"{decoded_token}", end="", flush=True)
            func_name += decoded_token
            encoded_prompt.append(best_token)
        self.__set_state(States.PARAMS)
        print()
        return dumps(func_name)

    def __get_current_parameter(self, encoded_prompt: list[int]) -> str:
        """Generate the value for the current parameter.

        Args:
            encoded_prompt: Tokenized prompt extended as values are generated.

        Returns:
            The generated parameter value followed by a comma and space.
        """
        from ..functions import get_options, parameter_ending
        transition_state: TransitionState = self.transition_state
        model: Llm = self.model
        parameter: str = ''
        max_token = 100
        if (
            transition_state.parameter_key and
            transition_state.parameter_key[1] in [Types.INT, Types.FLOAT]
        ):
            max_token = 10
        if (
            transition_state.parameter_key and
            transition_state.parameter_key[1] == Types.STRING
        ):
            parameter = '"'
            print('"', end="", flush=True)
        param_option = get_options(caller=self)
        while True:
            best_token = model.get_best_token(
                prompt=encoded_prompt,
                options=param_option
            )
            decoded_token: str = model.decode([best_token])
            max_token -= 1
            if transition_state.parameter_key and parameter_ending(
                max_token, parameter, decoded_token,
                transition_state.parameter_key[1]
            ):
                if transition_state.parameter_key[1] == Types.STRING:
                    decoded_token = decoded_token.split('"')[0] + '"'
                    print(f'{decoded_token}', end="", flush=True)
                    parameter += decoded_token
                    encoded_prompt.extend(model.encode_to_int(decoded_token))
                break
            print(f'{decoded_token}', end="", flush=True)
            parameter += decoded_token
            encoded_prompt.append(best_token)
        if (
            transition_state.parameter_key and
            transition_state.parameter_key[1] == Types.FLOAT
        ):
            casted_parameter = str(float(parameter))
            if "." not in parameter:
                print(".0", end="", flush=True)
            parameter = parameter.replace(parameter, casted_parameter)
        parameter += ', '
        print()
        return parameter

    def __call_parameters(self, call: str, func_name: str) -> str:
        """Generate JSON fields for the selected function's parameters.

        Args:
            call: User prompt describing the requested function call.
            func_name: Name of the selected function.

        Returns:
            The generated parameter fields, or ``"{}"`` if there are none.
        """
        from ..functions import get_function_parameters_keys
        model: Llm = self.model
        func_parameters: str = ""
        param_keys = get_function_parameters_keys(
            func_defs=self.func_defs,
            func_name=func_name
        )
        print('Parameters:', end="", flush=True)
        if param_keys:
            self.__set_state(States.PARAMS, param_keys[0])
        else:
            print(' {}\n')
            return "{}"
        print()
        prompt: str = self.__get_prompt(call, func_name=func_name)
        prompt += "{"
        prompt += f'"{param_keys[0][0]}":'
        if param_keys[0][1] == Types.STRING:
            prompt += '"'
        encoded_prompt: list[int] = model.encode_to_int(prompt)
        for i in range(len(param_keys)):
            k = param_keys[i]
            key = k[0]
            print(f'\t{key}: ', end="", flush=True)
            self.__set_state(States.PARAMS, k)
            if i > 0 and k[1] != Types.STRING:
                prompt_keys = model.encode_to_int(f', "{key}":')
                encoded_prompt.extend(prompt_keys)
            if i > 0 and k[1] == Types.STRING:
                prompt_keys = model.encode_to_int(f', "{key}":"')
                encoded_prompt.extend(prompt_keys)
            try:
                parameter = self.__get_current_parameter(encoded_prompt)
            except ValueError:
                raise ValueError
            func_parameters += f'"{key}": {parameter}'
        func_parameters = func_parameters.rstrip(', ')
        print()
        return '{' + func_parameters + '}'

    def call_functions(
        self, path_output: str = "data/output/function_calling_results.json"
    ) -> None:
        """Resolve configured prompts and save their function calls.

        Args:
            path_output: Destination path for the generated function calls.
        """
        from ..functions import (
            get_function_defs_struct, get_function_names, store_JSON
        )
        func_defs_struct = get_function_defs_struct(self.func_defs)
        func_names = get_function_names(self.func_defs)
        calls: list[dict[str, Any]] = []
        name: str = ""
        store_JSON(calls, path_output=path_output)
        raw_answer: str = ""
        for call in self.func_calls:
            try:
                raw_answer = '{"prompt":' + dumps(call.prompt)
                name = self.__call_name(
                    call=call.prompt,
                    func_defs=func_defs_struct,
                    func_names=func_names
                )
                if name.rstrip('"').lstrip('"') not in func_names:
                    raise NameError
                raw_answer += ', "name":' + name
                parameters = self.__call_parameters(
                    call=call.prompt,
                    func_name=loads(name)
                )
                raw_answer += ', "parameters":' + parameters + '}'
                calls.append(loads(raw_answer))
                store_JSON(calls, path_output=path_output)
            except JSONDecodeError as e:
                print(
                    f"[ERROR] - {JSONDecodeError.__name__}: "
                    f"the structure of '{name}' "
                    f"is an invalid json. ({e})"
                )
            except NameError:
                print(
                    f"[ERROR] - {NameError.__name__}: "
                    f"the function '{name}' "
                    "doesn't exist in the function definitions."
                )
            except ValueError as e:
                print(
                    f"\n[ERROR] - {e.__class__.__name__}."
                    "Can't store this function call."
                )
