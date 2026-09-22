#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   decoder.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/19 19:55:00 by varandri            #+#    #+#            #
#   Updated: 2026/09/22 19:05:44 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
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
        name: dict[str, str] = {}
        prompt_answer: str = '"name":"'
        raw_answer: str = ""
        raw_prompt = (
            "You are a function selector. "
            "You will select a function_name from "
            "a list of given function definitions. "
            "You will chose the function that match the one "
            "described in a given prompt. "
            f"Function Definitions: {get_func_defs(
                tuple(self.function_definitions)
            )}. "
            "{"
            f'"prompt": "{prompt}", '
            f"{prompt_answer}"
        )
        encoded_raw_prompt = self.llm.int_encode(raw_prompt)
        while True:
            best_token: int = self.llm.get_best_token(self, encoded_raw_prompt)
            if '"' in self.llm.decode(tuple([best_token])):
                prompt_answer += '", '
                break
            print(self.llm.decode(tuple([best_token])), end="", flush=True)
            prompt_answer += self.llm.decode(tuple([best_token]))
            raw_answer += self.llm.decode(tuple([best_token]))
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
            get_func_struct, get_keys, set_state_type, clean_answer
        )

        param_keys: list[str] = get_keys(
            tuple(self.function_definitions), func_name["raw"]
        )
        prompt_answer: str = "{" + f'"{param_keys[0]}":'
        raw_prompt = (
            "You are a parameter retriever. "
            "You will retrieve the parameters value of a function "
            "in a given prompt. The function structure will also "
            "be given to you for you to take reference on. "
            'end each found value with a ". '
            f"Function structure: {get_func_struct(
                tuple(self.function_definitions),
                func_name['raw']
            )}. "
            "{"
            f'"prompt": "{prompt}", '
            f'"{func_name["raw"]}", "parameters":{prompt_answer}'
        )
        encoded_raw_prompt = self.llm.int_encode(raw_prompt)
        i = 0
        while True:
            try:
                p_key: str = param_keys[i]
                set_state_type(p_key, self, func_name["raw"])
                if self.state.type == Types.NULL:
                    return '"parameters": null'
                best_token: int = self.llm.get_best_token(
                    self, encoded_raw_prompt
                )
                decoded_best_token: str = self.llm.decode(tuple([best_token]))
                if (
                    (
                        ',' in decoded_best_token
                        and (
                            self.state.type == Types.NUMBER
                            or self.state.type == Types.INT
                        )
                    ) or
                    (
                        '",' in decoded_best_token
                        and (
                            self.state.type == Types.STRING
                            or self.state.type == Types.BOOLEAN
                        )
                    )
                ):
                    added_prompt: str = (
                        f'{decoded_best_token} "{param_keys[i + 1]}":"'
                    )
                    if (
                        self.state.type == Types.NUMBER or
                        self.state.type == Types.INT
                    ):
                        added_prompt = added_prompt[:-1]
                    prompt_answer += added_prompt
                    encoded_raw_prompt.extend(
                        self.llm.int_encode(added_prompt)
                    )
                    i += 1
                    continue
                if "}" in decoded_best_token:
                    i += len(p_key)
                    continue
            except IndexError:
                prompt_answer += f'{decoded_best_token}' + "}"
                break
            encoded_raw_prompt.append(best_token)
            prompt_answer += self.llm.decode(tuple([best_token]))
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
