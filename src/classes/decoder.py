#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   decoder.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/19 19:55:00 by varandri            #+#    #+#            #
#   Updated: 2026/09/23 15:23:58 by varandri           ###   ########.fr      #
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
            is_ending_token
        )

        param_keys: list[str] = get_keys(
            self.function_definitions, func_name["raw"]
        )
        set_state_type(param_keys[0], self, func_name["raw"])
        func_struct: dict[str, Any] = get_func_struct(
            self.function_definitions,
            func_name['raw']
        )
        prompt_answer: str = "{" + f'"{param_keys[0]}":'
        raw_prompt = (
            "You are a parameter retriever. "
            "You will retrieve the parameters value of a function "
            "in a given prompt. The function structure will also "
            "be given to you for you to take reference on. "
            'end each found value with a ". '
            f"Function structure: {func_struct}. "
            "{"
            f'"prompt": "{prompt}", '
            f'"{func_name["raw"]}", "parameters":{prompt_answer}'
        )
        encoded_raw_prompt = self.llm.int_encode(raw_prompt)
        max_token: int = 150
        if self.state.type in [Types.INT, Types.NUMBER]:
            max_token = 9
        i = 0
        while True:
            try:
                p_key: str = param_keys[i]
                if self.state.type == Types.NULL:
                    return '"parameters": null'
                best_token: int = self.llm.get_best_token(
                    self, encoded_raw_prompt
                )
                decoded_best_token: str = self.llm.decode([best_token])
                max_token -= 1
                print(decoded_best_token, end="", flush=True)
                if is_ending_token(self.state, decoded_best_token, max_token):
                    decoded_best_token = '",'
                    if max_token <= 0 and self.state.type in [
                        Types.INT or Types.NUMBER
                    ]:
                        decoded_best_token = ","
                    added_prompt: str = (
                        f'{decoded_best_token} "{param_keys[i + 1]}":"'
                    )
                    if self.state.type in [Types.NUMBER, Types.INT]:
                        added_prompt = added_prompt[:-1]
                    prompt_answer += added_prompt
                    encoded_raw_prompt.extend(
                        self.llm.int_encode(added_prompt)
                    )
                    i += 1
                    p_key = param_keys[i]
                    set_state_type(p_key, self, func_name["raw"])
                    max_token = 150
                    if self.state.type in [Types.INT, Types.NUMBER]:
                        max_token = 9
                    continue
                if '"}' in decoded_best_token:
                    i += len(param_keys) + 142
                    continue
            except IndexError:
                prompt_answer += f'{decoded_best_token}' + '}'
                break
            encoded_raw_prompt.append(best_token)
            prompt_answer += self.llm.decode([best_token])
        prompt_answer = clean_answer(prompt_answer)
        return prompt_answer

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
