#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   decoder.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/19 19:55:00 by varandri            #+#    #+#            #
#   Updated: 2026/09/29 13:40:59 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any
    from .enums import States, Types
    from .models import (
        FunctionCalling, FunctionDefinition, DecoderState
    )
    from pydantic import BaseModel, Field, ConfigDict
    from .llm import Llm
    from json import loads, dump, JSONDecodeError
except (ModuleNotFoundError, KeyboardInterrupt) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}.")
    exit()


class Decoder(BaseModel):
    llm: Llm = Field(default=Llm())
    function_definitions: list[FunctionDefinition] = Field(...)
    function_callings: list[FunctionCalling] = Field(...)
    output_file: str = Field(default="data/output/function_calls.json")
    state: DecoderState = Field(default=DecoderState())
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __decode_name(
        self, prompt: str, func_defs: list[dict[str, Any]]
    ) -> dict[str, str]:
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
        name["prompt"] = prompt_answer
        name["raw"] = raw_answer
        self.state.state = States.PARAMS
        print('",\n', end="", flush=True)
        return name

    def __decode_parameters(
            self, func_name: dict[str, str], prompt: str
    ) -> str:
        from ..functions import (
            get_func_struct, get_keys, set_state_type, clean_answer,
            is_ending_token, get_next_parameter, clean_raw_param,
            clean_decoded
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
            f'"prompt": "{prompt}", '
            f'"{func_name["raw"]}", "parameters":{prompt_answer[0]}'
        )
        encoded_raw_prompt = self.llm.int_encode(raw_prompt)
        max_token = [150]
        if self.state.type in [Types.INT, Types.NUMBER]:
            max_token[0] = 9
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
                if (
                    '"}' in prompt_answer[0] and
                    self.state.type == Types.STRING
                    or
                    '}' in prompt_answer[0] and
                    self.state.type == Types.BOOLEAN
                ):
                    prompt_answer[0] += '}'
                    break
                best_token: int = self.llm.get_best_token(
                    self, encoded_raw_prompt
                )
                decoded_best_token = self.llm.decode([best_token])
                max_token[0] -= 1
                raw_param[0] += decoded_best_token
                clean_raw_param(raw_param)
                print(
                    clean_decoded(decoded_best_token, raw_param, self.state),
                    end="", flush=True
                )
                raw_param[0] = raw_param[0].lstrip()
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
                prompt_answer[0] += '}'
                break
            encoded_raw_prompt.append(best_token)
            prompt_answer[0] += self.llm.decode([best_token])
        prompt_answer[0] = clean_answer(prompt_answer[0])
        if '"' in prompt_answer[0][-2:]:
            print('"\n\t\t', end="", flush=True)
        else:
            print('\n\t\t', end="", flush=True)
        return prompt_answer[0]

    def show_funcs(self) -> None:
        from ..functions import get_func_defs, get_func_def_names

        print("[")
        json_calls: list[dict[str, Any]] = []
        func_defs: list[dict[str, Any]] = get_func_defs(
            self.function_definitions
        )
        func_def_names: list[str] = get_func_def_names(
            self.function_definitions
        )
        for i in range(len(self.function_callings)):
            try:
                func_calls: str = ""
                prompt = self.function_callings[i].prompt
                func_calls += '{"prompt": "' + prompt.replace('\"', "") + '", '
                print(
                    "\t{\n\t\t"f'"prompt": "{prompt}",\n\t\t',
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
                    "doesn't exist."
                )
        print('\n]')
        print(json_calls)
