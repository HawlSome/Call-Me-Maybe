#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   param_decoder_helpers.py                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/22 21:11:40 by varandri            #+#    #+#            #
#   Updated: 2026/09/24 15:01:47 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from ..classes import FunctionDefinition, Decoder
from ..classes.models import DecoderState
from typing import Any
from ..classes.enums import Types
from .func_def_mappers import (
    get_func_parameters
)


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
            '",' in decoded_best_token
            and state.type in [Types.STRING]
        ) or
        max_token <= 0
    )


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


def smart_cast(state: DecoderState, value: str) -> str:
    if state.type == Types.INT:
        value = str(int(value))
    if state.type in [Types.NUMBER, Types.FLOAT]:
        value = str(float(value))
    return value


def get_next_parameter(
    *,
    decoder: Decoder, func_name: str, param_keys: list[str],
    max_token: list[int], i: list[int], decoded_best_token: str,
    encoded_raw_prompt: list[int], prompt_answer: list[str]
) -> None:
    if max_token[0] <= 0 and decoder.state.type in [
        Types.INT or Types.NUMBER
    ]:
        decoded_best_token = ","
    if max_token[0] <= 0 and decoder.state.type == Types.STRING:
        decoded_best_token = '",'
    i[0] += 1
    p_key = param_keys[i[0]]
    set_state_type(p_key, decoder, func_name)
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
