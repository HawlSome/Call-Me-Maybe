#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   decoder.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/19 19:55:00 by varandri            #+#    #+#            #
#   Updated: 2026/09/22 14:59:10 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any, cast
    from .enums import States, Types
    from .models import (
        FunctionCalling, FunctionDefinition, FunctionParameters,
        DecoderState
    )
    from llm_sdk import Small_LLM_Model  # type: ignore
    from pydantic import BaseModel, Field, ConfigDict
    from numpy import argmax
except ModuleNotFoundError:
    raise ModuleNotFoundError
    quit()


class Decoder(BaseModel):
    model: Small_LLM_Model = Field(default=Small_LLM_Model())
    function_definitions: list[FunctionDefinition] = Field(...)
    function_callings: list[FunctionCalling] = Field(...)
    output_file: str = Field(default="data/output/function_calls.json")
    state: DecoderState = Field(default=DecoderState())
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __int_encode(self, string: str) -> list[int]:
        encoded: list[int] = []
        for token in self.model.encode(string)[0]:
            encoded.append(int(token))
        return encoded

    def __decode(self, tokens: list[int]) -> str:
        return str(self.model.decode(tokens))

    def __get_logits(self, tokens: list[int]) -> list[float]:
        return cast(
            list[float],
            self.model.get_logits_from_input_ids(tokens)
        )

    def __get_func_def_names(self) -> list[str]:
        names: list[str] = []
        for fd_name in self.function_definitions:
            fd: str = f'{{"name": "{fd_name.name}"}}'
            names.append(fd)
        return names

    def __get_func_defs(self) -> list[dict[str, Any]]:
        func_defs: list[dict[str, Any]] = []
        for fnd in self.function_definitions:
            func_defs.append(self.__get_func_struct(fnd.name))
        return func_defs

    def __get_func_struct(self, func_name: str) -> dict[str, Any]:
        def get_parameters(
            func_parameters: list[FunctionParameters]
        ) -> dict[str, Any] | str:
            params: dict[str, Any] | str = {}
            for param in func_parameters:
                if param.key and not isinstance(params, str):
                    params[param.key] = param.value
                else:
                    params = "null"
            return params

        func_struct: dict[str, Any] = {}
        for func in self.function_definitions:
            if func.name == func_name:
                name = func_name
                description = func.description
                if func.parameters:
                    parameters = get_parameters(func.parameters)
                else:
                    parameters = None
                returns = func.returns
                func_struct["name"] = name
                func_struct["description"] = description
                func_struct["parameters"] = parameters
                func_struct["returns"] = returns
        return func_struct

    def __get_func_parameters(self, func_name: str) -> dict[str, Any]:
        param = cast(
            dict[str, Any], self.__get_func_struct(func_name)["parameters"]
        )
        return param

    def __get_best_token(self, prompt: str, logits: list[float]) -> int:
        def mask_logits(logits: list[float]) -> list[float]:
            def get_encoded_func_def_names() -> list[list[int]]:
                encoded_names: list[list[int]] = []
                for name in self.__get_func_def_names():
                    encoded_names.append(
                        self.__int_encode(name)
                    )
                return encoded_names

            def get_encoded_numeric_mask() -> list[int]:
                encoded_numeric_mask: list[int] = []
                for ch in '-".,0123456789':
                    encoded_numeric_mask.extend(self.__int_encode(ch))
                return encoded_numeric_mask

            def get_encoded_str_mask() -> list[int]:
                encoded_str_mask: list[int] = []
                for ch in '\"':
                    encoded_str_mask.extend(self.__int_encode(ch))
                return encoded_str_mask

            def get_encoded_boolen_mask() -> list[list[int]]:
                encoded_bool_mask: list[list[int]] = []
                for boolean in ["true", "false", '"', "}", ","]:
                    encoded_bool_mask.append(self.__int_encode(boolean))
                return encoded_bool_mask

            masked_logits = [float("-inf") for _ in logits]
            if self.state.state == States.NAME:
                for enc_names in get_encoded_func_def_names():
                    for token in enc_names:
                        masked_logits[token] = logits[token]
            if self.state.state == States.PARAMS:
                if (
                    self.state.type == Types.NUMBER or
                    self.state.type == Types.INT or
                    self.state.type == Types.FLOAT
                ):
                    for token in get_encoded_numeric_mask():
                        masked_logits[token] = logits[token]
                if self.state.type == Types.STRING:
                    for token in get_encoded_str_mask():
                        logits[token] = float("-inf")
                        masked_logits = logits
                if self.state.type == Types.BOOLEAN:
                    for bool_values in get_encoded_boolen_mask():
                        for token in bool_values:
                            masked_logits[token] = logits[token]
            return masked_logits

        masked_logits = mask_logits(logits)
        return int(argmax(masked_logits))

    def __decode_name(self, prompt: str) -> dict[str, str]:
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
            f"Function Definitions: {self.__get_func_defs()}. "
            f'Prompt: {prompt}. '
            f"{prompt_answer}"
        )
        encoded_raw_prompt = self.__int_encode(raw_prompt)
        while True:
            logits: list[float] = self.__get_logits(encoded_raw_prompt)
            best_token: int = self.__get_best_token("", logits)
            if '"' in self.__decode([best_token]):
                prompt_answer += '", '
                break
            print(self.__decode([best_token]), end="", flush=True)
            prompt_answer += self.__decode([best_token])
            raw_answer += self.__decode([best_token])
            encoded_raw_prompt.append(best_token)
        name["prompt"] = prompt_answer
        name["raw"] = raw_answer
        self.state.state = States.PARAMS
        print()
        return name

    def __decode_parameters(
            self, func_name: dict[str, str], prompt: str
    ) -> str:
        def get_keys() -> list[str]:
            try:
                keys: list[str] = []
                param_structure: dict[str, Any] = (
                    self.__get_func_parameters(func_name["raw"])
                )
                keys.extend(list(param_structure.keys()))
                return keys
            except Exception:
                return ["null"]

        def get_type(key: str) -> str:
            k_type: str = ""
            param_structure: dict[str, Any] = (
                self.__get_func_parameters(func_name["raw"])
            )
            k_type = param_structure[key]["type"]
            return k_type

        def set_state_type(key: str) -> None:
            try:
                k_type: str = get_type(key).lower()
                if k_type in "string":
                    self.state.type = Types.STRING
                elif (
                    k_type in "number" or
                    k_type in "float"
                ):
                    self.state.type = Types.NUMBER
                elif k_type in "integer":
                    self.state.type = Types.INT
                elif k_type in "boolean":
                    self.state.type = Types.BOOLEAN
                elif k_type in "null":
                    self.state.type = Types.NULL
            except Exception:
                self.state.type = Types.NULL

        def clean_answer(prompt_answer: str) -> str:
            prompt_answer = prompt_answer.replace(",}", "}")
            prompt_answer = prompt_answer.replace("}}", "}")
            prompt_answer = prompt_answer.replace("}.}", "}")
            prompt_answer = prompt_answer.replace('""', '"')
            prompt_answer = prompt_answer.replace('" +"', '')
            prompt_answer = prompt_answer.replace(',"}', '}')
            prompt_answer = '"parameters": ' + prompt_answer
            return prompt_answer

        param_keys: list[str] = get_keys()
        prompt_answer: str = "{" + f'"{param_keys[0]}":'
        raw_prompt = (
            "You are a parameter retriever. "
            "You will retrieve the parameters value of a function "
            "in a given prompt. The function structure will also "
            "be given to you for you to take reference on. "
            'end each found value with a ". '
            f"Function structure: {self.__get_func_struct(func_name['raw'])}. "
            f"Prompt: {prompt}."
            f'"{func_name["raw"]}", "params": {prompt_answer}'
        )
        encoded_raw_prompt = self.__int_encode(raw_prompt)
        i = 0
        while True:
            try:
                p_key: str = param_keys[i]
                set_state_type(p_key)
                if self.state.type == Types.NULL:
                    return '"parameters": null'
                logits: list[float] = self.__get_logits(encoded_raw_prompt)
                best_token: int = self.__get_best_token(prompt, logits)
                decoded_best_token: str = self.__decode([best_token])
                print(decoded_best_token, end="", flush=True)
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
                        self.__int_encode(added_prompt)
                    )
                    i += 1
                    continue
                if "}" in decoded_best_token:
                    i += len(p_key)
                    continue
            except IndexError:
                prompt_answer += f'{decoded_best_token}'
                break
            encoded_raw_prompt.append(best_token)
            prompt_answer += self.__decode([best_token])
        print(prompt_answer)
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
