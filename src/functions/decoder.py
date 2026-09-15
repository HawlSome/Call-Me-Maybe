# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   decoder.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/16 00:09:28 by varandri            #+#    #+#            #
#   Updated: 2026/09/16 00:50:25 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from llm_sdk import Small_LLM_Model  # type: ignore
from ..classes import Function_definition
from ..functions import int_encoder, encode_fn_def_name, mask_logits
from numpy import argmax


def get_func_name(
    model: Small_LLM_Model,
    prompt: str, fn_defs: list[Function_definition]
) -> str:
    raw_prompt: str = (
        "You are a function selector, you will select a name from one "
        "of the following list of functions that already have a function "
        "name , description, parameters and also the return type."
        "your choice will be based from an asked fuction from a prompt. "
        f"prompt: {prompt}. "
        f"functions definition: {str(fn_defs)} ."
        f"selected function: "
    )
    func_name: str = ""
    encoded_prompt: list[int] = int_encoder(model, raw_prompt)
    encoded_fn_def_name: list[list[int]] = []
    encode_fn_def_name(model, fn_defs, encoded_fn_def_name)
    valid_fn_def_name: list[str] = [
        str(fn_def.name) for fn_def in fn_defs
    ]
    while True:
        raw_logits: list[float] = (
            model.get_logits_from_input_ids(encoded_prompt)
        )
        masked_logits: list[float] = (
            mask_logits(raw_logits, encoded_fn_def_name)
        )
        func_name += model.decode(int(argmax(masked_logits)))
        encoded_prompt.append(int(argmax(masked_logits)))
        if func_name in valid_fn_def_name:
            break
    return func_name
