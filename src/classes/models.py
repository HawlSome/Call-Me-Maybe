#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   models.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 19:17:30 by varandri            #+#    #+#            #
#   Updated: 2026/10/05 22:47:53 by varandri           ###   ########.fr      #
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
    parameters: dict[str, dict[str, str]] | None = Field(...)
    returns: dict[str, str] = Field(...)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def parameters_validator(self) -> "FunctionDefinition":
        """Validate the function parameters schema."""
        if self.parameters:
            for types in self.parameters.values():
                if len(types.keys()) > 1 or not types.get("type"):
                    raise ValueError(
                        "The format of parameters in functions"
                        " definition is invalid"
                    )
        else:
            self.parameters = None
        return self

    @model_validator(mode="after")
    def returns_validator(self) -> "FunctionDefinition":
        """Validate the function return schema."""
        if not len(self.returns.keys()):
            raise ValueError(
                "The format of returns in functions definition is invalid"
            )
        if not self.returns.get("type") and not self.returns.get("TYPE"):
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


class TransitionState(BaseModel):
    """Runtime state tracking for the decoder.

    Attributes:
        state: Active decoding stage, such as name selection or parameter
            extraction.
        type: Current expected parameter type.
    """
    state: States = Field(default=States.NAME)
    parameter_key: tuple[str, Types] | None = Field(default=None)