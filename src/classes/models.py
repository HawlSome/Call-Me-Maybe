# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   models.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 19:17:30 by varandri            #+#    #+#            #
#   Updated: 2026/09/18 17:31:19 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any
    from enum import Enum
    from pydantic import BaseModel, Field, ConfigDict, model_validator
    from llm_sdk import Small_LLM_Model
except ModuleNotFoundError:
    raise ModuleNotFoundError
    exit()


class States(Enum):
    NAME = "name"
    PARAMS = "params"


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
    state: States = Field(default=States.NAME)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __int_encoder(self, string: str) -> list[int]:
        encoded: list[int] = []
        for token in self.model.encode(string)[0]:
            encoded.append(int(token))
        return encoded

    def __get_func_def_names(self) -> list[str]:
        names: list[str] = []
        for fd_name in self.Function_Definition:
            fd: str = f'{{"name": "{fd_name.name}"}}'
            names.append(fd)
        return names

    def __get_encoded_func_def_names(self) -> list[list[int]]:
        encoded_names: list[list[int]] = []
        for name in self.__get_func_def_names():
            encoded_names.append(
                self.__int_encoder(name)
            )
        return encoded_names

    def show_funcs(self) -> None:
        print(self.function_definitions)

    def __mask_logits(
        self, logits: list[float]
    ) -> list[float]:
        masked_logits = [float("-inf") for _ in logits]
        if self.state == States.NAME:
            for enc_names in self.__get_encoded_func_def_names():
                for token in enc_names:
                    masked_logits[token] = logits[token]
        return masked_logits

    def decode(self) -> None:
        pass
