#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   models.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 19:17:30 by varandri            #+#    #+#            #
#   Updated: 2026/09/19 18:34:23 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any, cast
    from enum import Enum
    from pydantic import BaseModel, Field, ConfigDict, model_validator
    from llm_sdk import Small_LLM_Model  # type: ignore
    from numpy import argmax
except ModuleNotFoundError:
    raise ModuleNotFoundError
    exit()


class States(Enum):
    NAME = "name"
    PARAMS = "params"


class Types(Enum):
    STRING = "string"
    NUMBER = "number"
    NULL = ""


class Function_Parameters(BaseModel):
    key: str = Field(...)
    value: dict[str, str] = Field(...)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def value_validator(self) -> "Function_Parameters":
        if len(self.value) > 1:
            raise ValueError(
                "The format of parameters in functions definition is invalid"
            )
        if not self.value.get("type"):
            raise ValueError(
                "The format of parameters in functions definition is invalid"
            )
        return self


class Function_Definition(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    parameters: list[Function_Parameters] = Field(...)
    returns: dict[str, str] = Field(...)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def returns_validator(self) -> "Function_Definition":
        if len(self.returns) > 1:
            raise ValueError(
                "The format of returns in functions definition is invalid"
            )
        if not self.returns.get("type"):
            raise ValueError(
                "The format of returns in functions definition is invalid"
            )
        return self


class Function_Calling(BaseModel):
    prompt: str = Field(...)
    model_config = ConfigDict(extra="forbid")


class Function_Output(BaseModel):
    prompt: str = Field(...)
    name: str = Field(...)
    parameters: dict[str, Any]
    model_config = ConfigDict(extra="forbid")


class Decoder(BaseModel):
    model: Small_LLM_Model = Field(default=Small_LLM_Model())
    function_definitions: list[Function_Definition] = Field(...)
    function_callings: list[Function_Calling] = Field(...)
    output_file: str = Field(default="data/output/function_calls.json")
    state: dict[str, States | Types] = Field(
        default={"state": States.NAME, "type": Types.NULL}
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def state_validator(self) -> "Decoder":
        if len(self.state) != 2:
            raise ValueError(
                "The format of state in Decoder is invalid."
            )
        try:
            if (
                not isinstance(self.state["state"], States) or
                not isinstance(self.state["type"], Types)
            ):
                raise ValueError(
                    "The format of state in Decoder is invalid."
                )
        except Exception:
            raise ValueError(
                "The format of state in Decoder is invalid."
            )
        return self

    def __int_encode(self, string: str) -> list[int]:
        encoded: list[int] = []
        for token in self.model.encode(string)[0]:
            encoded.append(int(token))
        return encoded

    def __decode(self, tokens: list[int]) -> str:
        return str(self.model.decode(tokens))

    def __get_logits(self, tokens: list[int]) -> list[float]:
        return self.model.get_logits_from_input_ids(tokens)

    def __get_func_def_names(self) -> list[str]:
        names: list[str] = []
        for fd_name in self.function_definitions:
            fd: str = f'{{"name": "{fd_name.name}"}}'
            names.append(fd)
        return names

    def __get_func_struct(self, func_name: str) -> dict[str, Any]:
        def get_parameters(
            func_parameters: list[Function_Parameters]
        ) -> dict[str, Any]:
            params: dict[str, Any] = {}
            for param in func_parameters:
                params[param.key] = param.value
            return params

        func_struct: dict[str, Any] = {}
        for func in self.function_definitions:
            if func.name == func_name:
                name = func_name
                description = func.description
                parameters = get_parameters(func.parameters)
                returns = func.returns
                func_struct["name"] = name
                func_struct["description"] = description
                func_struct["parameters"] = parameters
                func_struct["returns"] = returns
        return func_struct

    def __get_func_defs(self) -> list[dict[str, Any]]:
        func_defs: list[dict[str, Any]] = []
        for fnd in self.function_definitions:
            func_defs.append(self.__get_func_struct(fnd.name))
        return func_defs

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
                numeric_mask: str = '0123456789.,-"'
                encoded_numeric_mask.extend(self.__int_encode(numeric_mask))
                return encoded_numeric_mask

            masked_logits = [float("-inf") for _ in logits]
            if self.state["state"] == States.NAME:
                for enc_names in get_encoded_func_def_names():
                    for token in enc_names:
                        masked_logits[token] = logits[token]
            if self.state["state"] == States.PARAMS:
                if self.state["types"] == Types.NUMBER:
                    for token in get_encoded_numeric_mask():
                        masked_logits[token] = logits[token]
            return masked_logits

        masked_logits = mask_logits(logits)
        return int(argmax(masked_logits))

    def __decode_name(self, prompt: str) -> dict[str, str]:
        name: dict[str, str] = {}
        prompt_answer: str = '{"name": "'
        raw_answer: str = ""
        raw_prompt = (
            "You are a function selector. "
            "You will select a function_name from "
            "a list of given function definitions. "
            "You will chose the function that match the one "
            "described in a given prompt. "
            f"Function Definitions: {self.__get_func_defs()}. "
            f"Prompt: {prompt}."
            f"{prompt_answer}"
        )
        encoded_raw_prompt = self.__int_encode(raw_prompt)
        while True:
            logits: list[float] = self.__get_logits(encoded_raw_prompt)
            best_token: int = self.__get_best_token("", logits)
            if '"' in self.__decode([best_token]):
                prompt_answer += '", '
                break
            prompt_answer += self.__decode([best_token])
            raw_answer += self.__decode([best_token])
            encoded_raw_prompt.append(best_token)
        name["prompt"] = prompt_answer
        name["raw"] = raw_answer
        self.state["state"] = States.PARAMS
        return name

    def __decode_parameters(self) -> Any:
        pass

    def function_call(self) -> None:
        pass

    def show_funcs(self) -> None:
        # print(self.__get_func_defs())
        # print()
        # print(self.__get_func_struct("fn_greet"))
        # print(self.__get_func_parameters("fn_greet"))
        func_name = self.__decode_name(
            self.function_callings[0].prompt
        )
        print(func_name)