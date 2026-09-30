#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   func_def_mappers.py                                  :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/22 19:05:07 by varandri            #+#    #+#            #
#   Updated: 2026/09/30 12:42:28 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any, cast
    from ..classes import (
        FunctionParameters, FunctionDefinition
    )
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


def get_func_def_names(
    function_definitions: list[FunctionDefinition]
) -> list[str]:
    names: list[str] = []
    for fd_name in function_definitions:
        fd: str = f'{{"name": "{fd_name.name}"}}'
        names.append(fd)
    return names


def get_func_defs(
    function_definitions: list[FunctionDefinition]
) -> list[dict[str, Any]]:
    func_defs: list[dict[str, Any]] = []
    for fnd in function_definitions:
        func_defs.append(get_func_struct(
            function_definitions, fnd.name)
        )
    return func_defs


def get_func_struct(
    function_definitions: list[FunctionDefinition], func_name: str
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


def get_func_parameters(
        function_definitions: list[FunctionDefinition], func_name: str
) -> dict[str, Any]:
    param = cast(
        dict[str, Any], get_func_struct(
            function_definitions, func_name
        )["parameters"]
    )
    return param
