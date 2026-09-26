#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   decoder.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/19 19:55:00 by varandri            #+#    #+#            #
#   Updated: 2026/09/26 11:35:19 by varandri           ###   ########.fr      #
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
except ModuleNotFoundError:
    raise ModuleNotFoundError


class Decoder(BaseModel):
    llm: Llm = Field(default=Llm())
    function_definitions: list[FunctionDefinition] = Field(...)
    function_callings: list[FunctionCalling] = Field(...)
    output_file: str = Field(default="data/output/function_calls.json")
    state: DecoderState = Field(default=DecoderState())
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __decode_name(self, prompt: str) -> dict[str, str]:
        from ..functions import get_func_defs

        self.state.state = States.NAME
        self.state.type = Types.NULL
        func_defs: list[dict[str, Any]] = get_func_defs(
            self.function_definitions
        )
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
        while True:
            best_token: int = self.llm.get_best_token(self, encoded_raw_prompt)
            if '"' in self.llm.decode([best_token]):
                prompt_answer += '", '
                break
            print(self.llm.decode([best_token]), end="", flush=True)
            prompt_answer += self.llm.decode([best_token])
            raw_answer += self.llm.decode([best_token])
            encoded_raw_prompt.append(best_token)
        name["prompt"] = prompt_answer
        name["raw"] = raw_answer
        self.state.state = States.PARAMS
        print()
        return name

    def __decode_parameters(
            self, func_name: dict[str, str], prompt: str
    ) -> str:
        from ..functions import (
            get_func_struct, get_keys, set_state_type, clean_answer,
            is_ending_token, get_next_parameter, clean_raw_param,
            clean_decoded, smart_cast
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
        while True:
            try:
                if self.state.type == Types.NULL:
                    return '"parameters": null'
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
                if (
                    '"}' in decoded_best_token and
                    self.state.type == Types.STRING
                    or
                    '}' in decoded_best_token and
                    self.state.type == Types.BOOLEAN
                ):
                    raise IndexError
            except IndexError:
                prompt_answer[0] += f'{decoded_best_token}' + '}'
                break
            encoded_raw_prompt.append(best_token)
            prompt_answer[0] += self.llm.decode([best_token])
        prompt_answer[0] = clean_answer(prompt_answer[0])
        return prompt_answer[0]

    def function_call(self) -> None:
        pass

    def show_funcs(self) -> None:
        for func_calling in self.function_callings:
            prompt = func_calling.prompt
            func_name = self.__decode_name(
                prompt
            )
            func_params = self.__decode_parameters(
                func_name, prompt
            )
            print(f"{func_name['prompt']} {func_params}")
