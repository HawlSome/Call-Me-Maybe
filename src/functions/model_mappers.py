#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   model_mappers.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:29:07 by varandri            #+#    #+#            #
#   Updated: 2026/10/14 13:48:44 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Map function definitions to names, structures, and parameter metadata."""

try:
    from typing import Any, cast
    from ..classes import FunctionDefinition
    from ..classes import Types
    from json import dumps
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
    """Find the parameter schema for a function by name.

    Args:
        func_defs: Function definitions to search.
        func_name: Name of the function to find.

    Returns:
        The function's parameter schema, or ``None`` if it has no parameters
        or is not found.
    """
    for func in func_defs:
        if func.name == func_name:
            return func.parameters
    return None


def get_function_names(func_defs: list[FunctionDefinition]) -> list[str]:
    """Get the names of the supplied function definitions.

    Args:
        func_defs: Function definitions whose names should be returned.

    Returns:
        Function names in definition order.
    """
    return [
        dumps(func.name).rstrip('"').lstrip('"') for func in func_defs
    ]


def get_function_struct(
        func_defs: list[FunctionDefinition], func_name: str
) -> dict[str, Any] | None:
    """Get the serialized structure of a function definition.

    Args:
        func_defs: Function definitions to search.
        func_name: Name of the function to serialize.

    Returns:
        The function definition as a dictionary, or ``None`` if not found.
    """
    for func in func_defs:
        if func.name == func_name:
            return func.model_dump()
    return None


def get_function_defs_struct(
    func_defs: list[FunctionDefinition]
) -> list[dict[str, Any]]:
    """Serialize all supplied function definitions.

    Args:
        func_defs: Function definitions to serialize.

    Returns:
        Serialized definitions in input order.
    """
    return cast(
        list[dict[str, Any]],
        [
            get_function_struct(func_defs, func_name)
            for func_name in get_function_names(func_defs)
        ]
    )


def get_function_parameters_keys(
    func_defs: list[FunctionDefinition], func_name: str
) -> list[tuple[str, Types]] | None:
    """Get parameter names paired with their decoder types.

    Args:
        func_defs: Function definitions to search.
        func_name: Name of the function whose parameters are requested.

    Returns:
        Parameter name and type pairs, or ``None`` if there are no parameters
        or the function is not found.
    """
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
    return function_keys
