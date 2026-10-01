#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   models.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 19:17:30 by varandri            #+#    #+#            #
#   Updated: 2026/10/01 23:19:08 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Data models for function definitions and decoder state.

This module defines the core Pydantic models used to represent function
metadata, input prompts, decoded outputs, and the runtime state of the
decoder.
"""

try:
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
    """Definition of a single function parameter.

    Attributes:
        key: Name of the parameter.
        value: Parameter schema metadata, including its expected type.
    """

    key: str = Field(...)
    value: dict[str, str] = Field(...)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def value_validator(self) -> "FunctionParameters":
        """Validate the parameter schema."""
        if not self.value:
            raise ValueError(
                "The format of parameters in functions definition is invalid"
            )
        if not self.value.get("type") or not self.value.get("TYPE"):
            raise ValueError(
                "The format of parameters in functions definition is invalid"
            )
        return self


class FunctionDefinition(BaseModel):
    """Definition of a callable function.

    Attributes:
        name: Name of the function.
        description: Human-readable description of the function behavior.
        parameters: List of parameter definitions accepted by the function.
        returns: Return schema describing the output value.
    """

    name: str = Field(...)
    description: str = Field(...)
    parameters: list[FunctionParameters] | None = Field(...)
    returns: dict[str, str] = Field(...)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def returns_validator(self) -> "FunctionDefinition":
        """Validate the function return schema."""
        if not len(self.returns.keys()):
            raise ValueError(
                "The format of returns in functions definition is invalid"
            )
        if not self.returns.get("type") or not self.returns.get("TYPE"):
            raise ValueError(
                "The format of returns in functions definition is invalid"
            )
        return self


class FunctionCalling(BaseModel):
    """A prompt paired with a function call request.

    Attributes:
        prompt: User prompt to be translated into a function call.
    """

    prompt: str = Field(...)
    model_config = ConfigDict(extra="forbid")


class DecoderState(BaseModel):
    """Runtime state tracking for the decoder.

    Attributes:
        state: Active decoding stage, such as name selection or parameter
            extraction.
        type: Current expected parameter type.
    """

    state: States = Field(default=States.NAME)
    type: Types = Field(default=Types.NULL)
