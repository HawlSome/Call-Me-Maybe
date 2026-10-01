#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   param_decoder_helpers.py                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/22 21:11:40 by varandri            #+#    #+#            #
#   Updated: 2026/10/01 18:13:15 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Helper utilities for parameter decoding.

This module provides functions used to normalize decoded values, identify
parameter boundaries, and move the decoder between parameter fields.
"""

try:
    from ..classes import FunctionDefinition, Decoder
    from ..classes.models import DecoderState
    from typing import Any
    from ..classes.enums import Types
    from .func_def_mappers import (
        get_func_parameters
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


def get_keys(
    function_definitions: list[FunctionDefinition], func_name: str
) -> list[str]:
    """Return the parameter names for a selected function.

    Args:
        function_definitions: Available function definitions.
        func_name: Name of the selected function.

    Returns:
        A list of parameter names. Returns ``["null"]`` if no parameter
        structure can be resolved.
    """
    try:
        keys: list[str] = []
        param_structure: dict[str, Any] = (
            get_func_parameters(function_definitions, func_name)
        )
        keys.extend(list(param_structure.keys()))
        return keys
    except Exception:
        return ["null"]


def __get_type(
    key: str,
    function_definitions: list[FunctionDefinition], func_name: str
) -> str:
    """Resolve the declared type for a parameter key.

    Args:
        key: Parameter name.
        function_definitions: Available function definitions.
        func_name: Name of the selected function.

    Returns:
        The parameter type as a string.
    """
    k_type: str = ""
    param_structure: dict[str, Any] = (
        get_func_parameters(function_definitions, func_name)
    )
    k_type = param_structure[key]["type"]
    return k_type


def set_state_type(key: str, decoder: Decoder, func_name: str) -> None:
    """Set the decoder state according to the selected parameter type.

    Args:
        key: Parameter name to inspect.
        decoder: Current decoder instance.
        func_name: Function whose parameter schema is being used.
    """
    try:
        k_type: str = __get_type(
            key, decoder.function_definitions, func_name
        ).lower()
        if k_type in "string":
            decoder.state.type = Types.STRING
        elif (
            k_type in "number" or
            k_type in "float"
        ):
            decoder.state.type = Types.NUMBER
        elif k_type in "integer":
            decoder.state.type = Types.INT
        elif k_type in "boolean":
            decoder.state.type = Types.BOOLEAN
        elif k_type in "null":
            decoder.state.type = Types.NULL
    except Exception:
        decoder.state.type = Types.NULL


def is_ending_token(
    state: DecoderState, decoded_best_token: str, max_token: int
) -> bool:
    """Determine whether the current token ends the active parameter value.

    Args:
        state: Decoder state.
        decoded_best_token: Last decoded token.
        max_token: Remaining token budget.

    Returns:
        True if the token marks the end of the parameter value.
    """
    return (
        (
            ',' in decoded_best_token
            and state.type in [Types.NUMBER, Types.INT, Types.BOOLEAN]
        ) or
        (
            '.' in decoded_best_token
            and state.type == Types.INT
        ) or
        (
            '",' in decoded_best_token
            and state.type in [Types.STRING]
        ) or
        max_token <= 0
    )


def is_ending_parameters(
    state: DecoderState, decoded_best_token: str, prompt_answer: str
) -> bool:
    """Determine whether all the parameters are generated.

    Args:
        state: Decoder state.
        decoded_best_token: Last decoded token.
        max_token: Remaining token budget.

    Returns:
        True if the token mark that all parameters were generated.
    """
    return (
        '"}' in decoded_best_token and
        state.type == Types.STRING
        or
        '"}' in prompt_answer and
        state.type == Types.STRING
        or
        '}' in decoded_best_token and
        state.type == Types.BOOLEAN
        or
        '}' in prompt_answer and
        state.type == Types.BOOLEAN
    )


def smart_strip(
    decoded_best_token: str, raw_param: list[str],
    state: DecoderState
) -> str:
    """Normalize a decoded token value for output formatting.

    Args:
        decoded_best_token: Token string received from the model.
        raw_param: Accumulated raw parameter content.
        state: Decoder state containing the current type.

    Returns:
        Striped token string.
    """
    if raw_param[0].startswith(' "'):
        decoded_best_token = decoded_best_token.lstrip(' "')
        raw_param[0] = raw_param[0].lstrip(' "')
    return decoded_best_token


def smart_cast(state: DecoderState, value: str) -> str:
    """Cast a decoded value to the expected numeric representation.

    Args:
        state: Decoder state containing the expected parameter type.
        value: Decoded value as text.

    Returns:
        Cast value as a string.
    """
    if state.type in [Types.NUMBER, Types.FLOAT]:
        value = str(float(value))
    return value


def get_next_parameter(
    *,
    decoder: Decoder, func_name: str, param_keys: list[str],
    max_token: list[int], i: list[int], decoded_best_token: str,
    encoded_raw_prompt: list[int], prompt_answer: list[str],
    raw_param: list[str], casted_param: list[str]
) -> None:
    """Advance the decoder to the next parameter key.

    Args:
        decoder: Current decoder instance.
        func_name: Function currently being decoded.
        param_keys: Parameter names for the selected function.
        max_token: Remaining token budget for the current parameter.
        i: Current parameter index.
        decoded_best_token: Last decoded token.
        encoded_raw_prompt: Prompt token buffer.
        prompt_answer: Accumulated prompt answer string.
        raw_param: Raw parameter value buffer.
        casted_param: Casted parameter value buffer.
    """
    if max_token[0] <= 0 and decoder.state.type in [
        Types.INT or Types.NUMBER
    ]:
        decoded_best_token = ","
    if max_token[0] <= 0 and decoder.state.type == Types.STRING:
        decoded_best_token = '",'
    casted_param[0] = smart_cast(decoder.state, raw_param[0])
    prompt_answer[0] = prompt_answer[0].replace(
        raw_param[0], casted_param[0]
    )
    if len(casted_param[0]) > len(raw_param[0]):
        casted_param[0] = casted_param[0].replace(raw_param[0], "")
    else:
        casted_param[0] = raw_param[0].replace(casted_param[0], "")
    print(f"{casted_param[0]}", end="", flush=True)
    if decoder.state.type == Types.STRING:
        delimiter = decoded_best_token.rsplit('"')[0]
        decoded_best_token = f'{delimiter}",'
        print(f'{delimiter}"', end="", flush=True)
    i[0] += 1
    p_key = param_keys[i[0]]
    set_state_type(p_key, decoder, func_name)
    print(f',\n\t\t\t\t"{p_key}": ', end="", flush=True)
    if decoder.state.type == Types.STRING:
        print('"', end="", flush=True)
    if decoded_best_token == ".":
        decoded_best_token = ","
    added_prompt: str = (
        f'{decoded_best_token} "{param_keys[i[0]]}":"'
    )
    if decoder.state.type in [
        Types.NUMBER, Types.INT, Types.BOOLEAN
    ]:
        added_prompt = added_prompt[:-1]
    prompt_answer[0] += added_prompt
    encoded_raw_prompt.extend(
        decoder.llm.int_encode(added_prompt)
    )
    max_token[0] = 100
    if decoder.state.type in [Types.INT, Types.NUMBER]:
        max_token[0] = 15
