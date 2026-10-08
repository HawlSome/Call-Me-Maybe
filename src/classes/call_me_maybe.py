#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   call_me_maybe.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:20:32 by varandri            #+#    #+#            #
#   Updated: 2026/10/08 19:23:00 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any
    from .enums import States, Types
    from pydantic import BaseModel, Field, ConfigDict
    from .models import FunctionCalling, FunctionDefinition, TransitionState
    from .llm_wrapper import Llm
    from json import dumps
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
    func_defs: list[FunctionDefinition] = Field(default=...)
    func_calls: list[FunctionCalling] = Field(default=...)
    model: Llm = Field(default=Llm())
    transition_state: TransitionState = Field(default=TransitionState())
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __set_state(
        self, state: States = States.NAME,
        param_keys: tuple[str, Types] | None = None
    ) -> None:
        transition_state: TransitionState = self.transition_state
        transition_state.state = state
        transition_state.parameter_key = param_keys

    def __get_prompt(
        self, call: str, func_defs: list[dict[str, Any]] = [],
        func_name: str = ""
    ) -> str:
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
            'the value must follow json strucutre value.\n'
            f"Function structure: {func_struct}.\n"
            "{"
            f'"prompt": "{call}", "name": '
            f'"{func_name}", "parameters":'
        )

    def __call_name(
        self, call: str, func_defs: list[dict[str, Any]],
        func_names: list[str]
    ) -> str:
        from ..functions import get_options
        self.__set_state()
        print(f'Prompt: "{call}".')
        print("Function Name: ", end="", flush=True)
        model: Llm = self.model
        func_name = ""
        max_token = 20
        name_options = get_options(caller=self)
        prompt = self.__get_prompt(call, func_defs)
        encoded_prompt = model.encode_to_int(prompt)
        while True:
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
        print("\n")
        return dumps(func_name)

    def __get_current_parameter(self, encoded_prompt: list[int]) -> str:
        from ..functions import get_options
        transition_state: TransitionState = self.transition_state
        model: Llm = self.model
        parameter: str = ''
        max_token = 100
        if (
            transition_state.parameter_key and
            transition_state.parameter_key[1] in [Types.INT, Types.FLOAT]
        ):
            max_token = 10
        param_option = get_options(caller=self)
        while True:
            best_token = model.get_best_token(
                prompt=encoded_prompt,
                options=param_option
            )
            decoded_token = model.decode([best_token])
            max_token -= 1
            if (
                max_token <= 0 or
                (
                    parameter.startswith('"') and
                    parameter.endswith('"')
                )
            ):
                break
            print(f'{decoded_token}', end="", flush=True)
            parameter += decoded_token
            encoded_prompt.append(best_token)
        parameter += ', '
        print()
        return parameter

    def __call_parameters(self, call: str, func_name: str) -> str:
        from ..functions import get_function_parameters_keys
        model: Llm = self.model
        func_parameters: str = ""
        param_keys = get_function_parameters_keys(
            func_defs=self.func_defs,
            func_name=func_name
        )
        if param_keys:
            self.__set_state(States.PARAMS, param_keys[0])
        else:
            return "null"
        prompt: str = self.__get_prompt(call, func_name=func_name)
        prompt += " {" + f'"{param_keys[0][0]}":'
        encoded_prompt = model.encode_to_int(prompt)
        print('Parameters:')
        for k in param_keys:
            key = k[0]
            print(f'\t{key}: ', end="", flush=True)
            self.__set_state(States.PARAMS, k)
            parameter = self.__get_current_parameter(encoded_prompt)
            func_parameters += f'"{key}": {parameter}'
        func_parameters = func_parameters.rstrip(', ')
        print()
        return func_parameters

    def call_functions(self) -> None:
        from ..functions import get_function_defs_struct, get_function_names
        func_defs_struct = get_function_defs_struct(self.func_defs)
        func_names = get_function_names(self.func_defs)
        self.__call_name(
            call=self.func_calls[0].prompt,
            func_defs=func_defs_struct,
            func_names=func_names
        )
