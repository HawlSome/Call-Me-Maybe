#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   decoder.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/19 19:55:00 by varandri            #+#    #+#            #
#   Updated: 2026/10/01 18:07:00 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Decoder implementation for function-call generation.

This module is responsible for selecting the correct function name and
recovering the corresponding parameter values from model output.
"""

try:
    from typing import Any
    from .enums import States, Types
    from .models import (
        FunctionCalling, FunctionDefinition, DecoderState
    )
    from pydantic import BaseModel, Field, ConfigDict
    from .llm import Llm
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


class Decoder(BaseModel):
    """Decodes function names and parameters from model output.

    Attributes:
        llm: Language model instance used to generate tokens.
        function_definitions: Registered function definitions.
        function_callings: User prompts to decode into function calls.
        output_file: Destination JSON file for generated calls.
        state: Decoder run state and type tracking information.
    """

    llm: Llm = Field(default=Llm())
    function_definitions: list[FunctionDefinition] = Field(...)
    function_callings: list[FunctionCalling] = Field(...)
    output_file: str = Field(default="data/output/function_calls.json")
    state: DecoderState = Field(default=DecoderState())
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __decode_name(
        self, prompt: str, func_defs: list[dict[str, Any]]
    ) -> dict[str, str]:
        """Select the most relevant function from a prompt.

        Args:
            prompt: User prompt describing the target function.
            func_defs: Available function definitions used for selection.

        Returns:
            A dictionary containing the raw and formatted function name
            selection.
        """
        self.state.state = States.NAME
        self.state.type = Types.NULL
        name: dict[str, str] = {}
        prompt_answer: str = '"name": "'
        raw_answer: str = ""
        raw_prompt = (
            "You are a function selector. "
            "You will select a function_name from "
            "a list of given function definitions. "
            "You will chose the function that match the one "
            "described in a given prompt. "
            'the format is as ..."name": "fn_function_name"'
            f"Function Definitions: {func_defs}. Output:"
            '{'f'"prompt":"{prompt}", '
            f"{prompt_answer}"
        )
        encoded_raw_prompt = self.llm.int_encode(raw_prompt)
        print('"name": "', end="", flush=True)
        max_token: int = 20
        while True:
            best_token: int = self.llm.get_best_token(self, encoded_raw_prompt)
            max_token -= 1
            if '"' in self.llm.decode([best_token]) or max_token <= 0:
                prompt_answer += '", '
                break
            print(self.llm.decode([best_token]), end="", flush=True)
            prompt_answer += self.llm.decode([best_token])
            raw_answer += self.llm.decode([best_token])
            encoded_raw_prompt.append(best_token)
        prompt_answer = prompt_answer.replace(
            f'"{raw_answer}"', dumps(raw_answer)
        )
        name["prompt"] = prompt_answer
        name["raw"] = raw_answer
        self.state.state = States.PARAMS
        print('",\n', end="", flush=True)
        return name

    def __decode_parameters(
            self, func_name: dict[str, str], prompt: str
    ) -> str:
        """Decode the parameters associated with a selected function.

        Args:
            func_name: Dictionary with the selected function name and prompt.
            prompt: Original user prompt used to retrieve values.

        Returns:
            A JSON-like string containing the decoded function parameters.
        """
        from ..functions import (
            get_func_struct, get_keys, set_state_type,
            is_ending_token, get_next_parameter,
            smart_strip, is_ending_parameters
        )

        raw_param: list[str] = [""]
        param_keys: list[str] = get_keys(
            self.function_definitions, func_name["raw"]
        )
        set_state_type(param_keys[0], self, func_name["raw"])
        func_struct: dict[str, Any] = get_func_struct(
            self.function_definitions,
            func_name['raw']
        )
        prompt_answer: list[str] = ["{" + f'"{param_keys[0]}":']
        raw_prompt = (
            "You are a parameter retriever. "
            "You will retrieve the parameters value of a function "
            "in a given prompt. The function structure will also "
            "be given to you for you to take reference on. "
            'end each found value with a ". '
            f"Function structure: {func_struct}. "
            "{"
            f'"prompt": {dumps(prompt)}, '
            f'"{func_name["raw"]}", "parameters":{prompt_answer[0]}'
        )
        encoded_raw_prompt = self.llm.int_encode(raw_prompt)
        max_token = [150]
        if self.state.type in [Types.INT, Types.NUMBER]:
            max_token[0] = 15
        i = [0]
        decoded_best_token: str = ""
        casted_param: list[str] = [""]
        if self.state.type != Types.NULL:
            print(
                f'\t\t"parameters":'' {\n\t\t\t\t'f'"{param_keys[0]}": ',
                end="",
                flush=True
            )
            if self.state.type == Types.STRING:
                print('"', end="", flush=True)
        else:
            print('\t\t"parameters": null\n\t}', end="", flush=True)
            return '"parameters": null'
        while True:
            try:
                best_token: int = self.llm.get_best_token(
                    self, encoded_raw_prompt
                )
                decoded_best_token = self.llm.decode([best_token])
                if (is_ending_parameters(
                        self.state, decoded_best_token, prompt_answer[0]
                )):
                    if (
                        self.state.type ==
                        Types.STRING and not prompt_answer[0].endswith('"')
                    ):
                        prompt_answer[0] += '"'
                    prompt_answer[0] = prompt_answer[0].split('}', 1)[0] + '}'
                    break
                max_token[0] -= 1
                if is_ending_token(
                    self.state, decoded_best_token,
                    max_token[0]
                ):
                    get_next_parameter(
                        decoder=self, func_name=func_name["raw"],
                        param_keys=param_keys, max_token=max_token,
                        i=i, decoded_best_token=decoded_best_token,
                        encoded_raw_prompt=encoded_raw_prompt,
                        prompt_answer=prompt_answer, raw_param=raw_param,
                        casted_param=casted_param
                    )
                    raw_param[0] = ""
                    continue
            except IndexError:
                if prompt_answer[0].endswith(','):
                    prompt_answer[0] = prompt_answer[0].rsplit(',')[0]
                if (
                    self.state.type ==
                    Types.STRING and not prompt_answer[0].endswith('"')
                ):
                    prompt_answer[0] += '"'
                prompt_answer[0] += '}'
                break
            raw_param[0] += decoded_best_token
            print(
                smart_strip(decoded_best_token, raw_param, self.state),
                end="", flush=True
            )
            encoded_raw_prompt.append(best_token)
            prompt_answer[0] += self.llm.decode([best_token])
        if '"' in prompt_answer[0][-2:]:
            print('"\n\t\t', end="", flush=True)
        else:
            print('\n\t\t', end="", flush=True)
        return f'"parameters": {prompt_answer[0]}'

    def get_fun_calls(
        self, path_outdir: str = "data/output/function_calls.json"
    ) -> None:
        """Generate and store function calls from registered prompts.

        Args:
            path_outdir: Output path used to write the JSON result.

        Returns:
            None. The generated calls are printed and stored in a file.
        """
        from ..functions import get_func_defs, get_func_def_names, store_JSON
        json_calls: list[dict[str, Any]] = []
        func_defs: list[dict[str, Any]] = get_func_defs(
            self.function_definitions
        )
        func_def_names: list[str] = get_func_def_names(
            self.function_definitions
        )
        store_JSON(json_calls, path_outdir=path_outdir)
        print("[")
        for i in range(len(self.function_callings)):
            try:
                func_calls: str = ""
                prompt = self.function_callings[i].prompt
                func_calls += (
                    '{"prompt": ' + dumps(prompt) + ', '
                )
                print(
                    "\t{\n\t\t"f'"prompt": {dumps(prompt)},\n\t\t',
                    end="", flush=True
                )
                func_name = self.__decode_name(
                    prompt, func_defs
                )
                if '{' + func_name["prompt"][:-2] + '}' not in func_def_names:
                    raise NameError
                func_params = self.__decode_parameters(
                    func_name, prompt
                )
                func_calls += f"{func_name['prompt']} {func_params}""}"
                if "null" not in func_calls:
                    print("}\n\t}", end="", flush=True)
                if i < len(self.function_callings) - 1:
                    print(",")
                json_calls.append(
                    loads(func_calls)
                )
                store_JSON(json_calls, path_outdir=path_outdir)
            except JSONDecodeError as e:
                print(
                    f"[ERROR] - {JSONDecodeError.__name__}: "
                    f"the structure of '{func_name['raw']}' "
                    f"is an invalid json. ({e})"
                )
            except NameError:
                print(
                    f"[ERROR] - {NameError.__name__}: "
                    f"the function '{func_name['raw']}' "
                    "doesn't exist in the function definitions."
                )
        if not self.function_definitions:
            print(']')
            return
        print('\n]')
