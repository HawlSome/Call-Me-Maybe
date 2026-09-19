#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   models.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 19:17:30 by varandri            #+#    #+#            #
#   Updated: 2026/09/19 20:00:58 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any
    from .enums import States, Types
    from pydantic import BaseModel, Field, ConfigDict, model_validator
except ModuleNotFoundError:
    raise ModuleNotFoundError
    exit()


class FunctionParameters(BaseModel):
    key: str = Field(...)
    value: dict[str, str] = Field(...)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def value_validator(self) -> "FunctionParameters":
        if len(self.value) > 1:
            raise ValueError(
                "The format of parameters in functions definition is invalid"
            )
        if not self.value.get("type"):
            raise ValueError(
                "The format of parameters in functions definition is invalid"
            )
        return self


class FunctionDefinition(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    parameters: list[FunctionParameters] = Field(...)
    returns: dict[str, str] = Field(...)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def returns_validator(self) -> "FunctionDefinition":
        if len(self.returns) > 1:
            raise ValueError(
                "The format of returns in functions definition is invalid"
            )
        if not self.returns.get("type"):
            raise ValueError(
                "The format of returns in functions definition is invalid"
            )
        return self


class FunctionCalling(BaseModel):
    prompt: str = Field(...)
    model_config = ConfigDict(extra="forbid")


class FunctionOutput(BaseModel):
    prompt: str = Field(...)
    name: str = Field(...)
    parameters: dict[str, Any]
    model_config = ConfigDict(extra="forbid")


class DecoderState(BaseModel):
    state: States = Field(default=States.NAME)
    type: Types = Field(default=Types.NULL)
