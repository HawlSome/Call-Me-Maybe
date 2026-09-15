# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   models.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 19:17:30 by varandri            #+#    #+#            #
#   Updated: 2026/09/15 23:27:46 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any
    from pydantic import BaseModel, Field, ConfigDict
except ModuleNotFoundError:
    raise ModuleNotFoundError
    exit()


class Function_definition(BaseModel):
    name: str = Field(...)
    description: str = Field(...)
    parameters: dict[str, dict[str, str]] = Field(...)
    returns: dict[str, str] = Field(...)
    model_config = ConfigDict(extra="forbid")


class Function_calling(BaseModel):
    prompt: str = Field(...)
    model_config = ConfigDict(extra="forbid")


class Function_output(BaseModel):
    prompt: str = Field(...)
    name: str = Field(...)
    parameters: dict[str, Any]
    model_config = ConfigDict(extra="forbid")
