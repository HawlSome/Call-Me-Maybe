#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   func_def_mappers.py                                  :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/22 19:05:07 by varandri            #+#    #+#            #
#   Updated: 2026/09/30 13:50:03 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Function definition mapping utilities.

This module converts function metadata into a schema-friendly dictionary
structure used by the decoder and prompting workflow.
"""

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
    """Return the serialized function names from the definition list.

    Args:
        function_definitions: Function definitions to serialize.

    Returns:
        A list of JSON-like function name objects.
    """
    names: list[str] = []
    for fd_name in function_definitions:
        fd: str = f'{{"name": "{fd_name.name}"}}'
        names.append(fd)
    return names


def get_func_defs(
    function_definitions: list[FunctionDefinition]
) -> list[dict[str, Any]]:
    """Build the full function-definition payloads for model prompting.

    Args:
        function_definitions: Available function definitions.

    Returns:
        A list of dictionaries representing each function schema.
    """
    func_defs: list[dict[str, Any]] = []
    for fnd in function_definitions:
        func_defs.append(get_func_struct(
            function_definitions, fnd.name)
        )
    return func_defs


def get_func_struct(
    function_definitions: list[FunctionDefinition], func_name: str
) -> dict[str, Any]:
    """Return the function schema for a given function name.

    Args:
        function_definitions: Available function definitions.
        func_name: Name of the target function.

    Returns:
        A dictionary containing the function name, description, parameters,
        and return schema.
    """
    def get_parameters(
        func_parameters: list[FunctionParameters]
    ) -> dict[str, Any] | str:
        """Convert function parameters into a dictionary payload.

        Args:
            func_parameters: Parameter definitions for a function.

        Returns:
            A dictionary mapping parameter names to their schema, or "null"
            when no valid parameters are available.
        """
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
    """Return the parameter schema for a named function.

    Args:
        function_definitions: Available function definitions.
        func_name: Name of the target function.

    Returns:
        The parameter metadata dictionary for the selected function.
    """
    param = cast(
        dict[str, Any], get_func_struct(
            function_definitions, func_name
        )["parameters"]
    )
    return param
