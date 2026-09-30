#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   models.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 19:17:30 by varandri            #+#    #+#            #
#   Updated: 2026/09/30 12:42:38 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any
    from .enums import States, Types
    from pydantic import BaseModel, Field, ConfigDict, model_validator
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


class FunctionParameters(BaseModel):
    key: str = Field(...)
    value: dict[str, str] = Field(...)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def value_validator(self) -> "FunctionParameters":
        if not self.value:
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
    parameters: list[FunctionParameters] | None = Field(...)
    returns: dict[str, str] = Field(...)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def returns_validator(self) -> "FunctionDefinition":
        if not len(self.returns.keys()):
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
