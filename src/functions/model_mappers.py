#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   model_mappers.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:29:07 by varandri            #+#    #+#            #
#   Updated: 2026/10/05 21:13:18 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any
    from ..classes import FunctionDefinition
    from ..classes import Types
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


def __get_function_parameters(
    func_defs: list[FunctionDefinition], func_name: str
) -> dict[str, dict[str, str]] | None:
    for func in func_defs:
        if func.name == func_name:
            return func.parameters
    return None


def get_function_names(func_defs: list[FunctionDefinition]) -> list[str]:
    return [
        func.name for func in func_defs
    ]


def get_function_struct(
        func_defs: list[FunctionDefinition], func_name: str
) -> dict[str, Any] | None:
    for func in func_defs:
        if func.name == func_name:
            return func.model_dump()
    return None


def get_function_parameters_keys(
    func_defs: list[FunctionDefinition], func_name: str
) -> tuple[tuple[str, Types], ...] | None:
    func_parameters = __get_function_parameters(func_defs, func_name)
    function_keys: list[tuple[str, Types]] = []
    if not func_parameters:
        return None
    for key in func_parameters.keys():
        raw_type: str = func_parameters[key]["type"].lower()
        enum_type: Types
        if raw_type in "strings":
            enum_type = Types.STRING
        elif raw_type in "booleans":
            enum_type = Types.BOOLEAN
        elif raw_type in "integers":
            enum_type = Types.INT
        elif raw_type in "numbers" or raw_type in "floats":
            enum_type = Types.FLOAT
        else:
            enum_type = Types.STRING
        function_keys.append((key, enum_type))
    return tuple(function_keys)
