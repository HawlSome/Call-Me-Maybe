#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   param_decoder_helpers.py                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/22 21:11:40 by varandri            #+#    #+#            #
#   Updated: 2026/09/29 11:26:35 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from ..classes import FunctionDefinition, Decoder
    from ..classes.models import DecoderState
    from typing import Any
    from ..classes.enums import Types
    from .func_def_mappers import (
        get_func_parameters
    )
except (ModuleNotFoundError, KeyboardInterrupt) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}.")
    exit()


def get_keys(
    function_definitions: list[FunctionDefinition], func_name: str
) -> list[str]:
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
    k_type: str = ""
    param_structure: dict[str, Any] = (
        get_func_parameters(function_definitions, func_name)
    )
    k_type = param_structure[key]["type"]
    return k_type


def set_state_type(key: str, decoder: Decoder, func_name: str) -> None:
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


def clean_decoded(
    decoded_best_token: str, raw_param: list[str],
    state: DecoderState
) -> str:
    if raw_param[0].startswith(' '):
        decoded_best_token = decoded_best_token.lstrip()
    decoded_best_token = decoded_best_token.replace('",', '')
    decoded_best_token = decoded_best_token.replace('",', '')
    if state.type in [Types.INT, Types.BOOLEAN, Types.NUMBER]:
        decoded_best_token = decoded_best_token.replace(',', '')
    if state.type == Types.INT:
        decoded_best_token = decoded_best_token.replace('.', '')
    decoded_best_token = decoded_best_token.replace('"', '')
    decoded_best_token = decoded_best_token.replace('}', '')
    decoded_best_token = decoded_best_token.replace('\n', '')
    return decoded_best_token


def clean_answer(prompt_answer: str) -> str:
    prompt_answer = prompt_answer.replace(",}", "}")
    prompt_answer = prompt_answer.replace("}}", "}")
    prompt_answer = prompt_answer.replace("}\n}", "}")
    prompt_answer = prompt_answer.replace("}.}", "}")
    prompt_answer = prompt_answer.replace('""', '"')
    prompt_answer = prompt_answer.replace('" +"', '')
    prompt_answer = prompt_answer.replace(',"}', '}')
    prompt_answer = '"parameters": ' + prompt_answer
    return prompt_answer


def clean_raw_param(raw_param: list[str]) -> None:
    raw_param[0] = raw_param[0].replace(',', '')
    raw_param[0] = raw_param[0].replace('"', '')
    raw_param[0] = raw_param[0].replace('"}', '')
    raw_param[0] = raw_param[0].replace('\n', '')


def smart_cast(state: DecoderState, value: str) -> str:
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
        print('"', end="", flush=True)
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
    max_token[0] = 150
    if decoder.state.type in [Types.INT, Types.NUMBER]:
        max_token[0] = 9
