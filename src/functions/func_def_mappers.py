#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   func_def_mappers.py                                  :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/22 19:05:07 by varandri            #+#    #+#            #
#   Updated: 2026/09/22 21:12:07 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from functools import lru_cache
from typing import Any, cast
from ..classes import (
    FunctionParameters, FunctionDefinition
)


@lru_cache(maxsize=None)
def get_func_def_names(
    function_definitions: tuple[FunctionDefinition, ...]
) -> list[str]:
    names: list[str] = []
    for fd_name in function_definitions:
        fd: str = f'{{"name": "{fd_name.name}"}}'
        names.append(fd)
    return names


@lru_cache(maxsize=None)
def get_func_defs(
    function_definitions: tuple[FunctionDefinition, ...]
) -> list[dict[str, Any]]:
    func_defs: list[dict[str, Any]] = []
    for fnd in function_definitions:
        func_defs.append(get_func_struct(
            function_definitions, fnd.name)
        )
    return func_defs


@lru_cache(maxsize=None)
def get_func_struct(
    function_definitions: tuple[FunctionDefinition, ...], func_name: str
) -> dict[str, Any]:
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
    for func in function_definitions:
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


@lru_cache(maxsize=None)
def get_func_parameters(
        function_definitions: tuple[FunctionDefinition, ...], func_name: str
) -> dict[str, Any]:
    param = cast(
        dict[str, Any], get_func_struct(
            function_definitions, func_name
        )["parameters"]
    )
    return param
