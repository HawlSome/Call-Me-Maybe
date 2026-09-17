# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   encoding.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 15:59:16 by varandri            #+#    #+#            #
#   Updated: 2026/09/17 14:02:41 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from llm_sdk import Small_LLM_Model  # type: ignore
from ..classes import Function_definition


def int_encoder(model: Small_LLM_Model, string: str) -> list[int]:
    encoded: list[int] = []
    for token in model.encode(string)[0]:
        encoded.append(int(token))
    return encoded


def encode_fn_def_name(
    model: Small_LLM_Model,
    fn_defs: list[Function_definition], encoded_fn_defs_name: list[list[int]]
) -> None:
    for fn_def in fn_defs:
        func_name: str = f'{{"name": "{fn_def.name}"}}'
        encoded_fn_defs_name.append(
            int_encoder(model, func_name)
        )


def encode_fn_struct(
    model: Small_LLM_Model,
    fn_name: str,
    fn_defs: list[Function_definition],
    encoded_fn_struct: list[int]
) -> None:
    for fn_def in fn_defs:
        if fn_def.name == fn_name:
            encoded_fn_struct.extend(int_encoder(model, str(fn_def)))


# def encode_prompts(
#     model: Small_LLM_Model,
#     prompts: list[Function_calling], encoded_prompts: list[list[int]]
# ) -> None:
#     for prompt in prompts:
#         encoded_prompts.append(int_encoder(model, prompt.prompt))


# def get_token_logits(
#     model: Small_LLM_Model, tokens: list[int]
# ) -> dict[int, float]:
#     token_logits: dict[int, float] = {}
#     # logits = model.get_logits_from_input_ids(tokens)
#     # for i in len(logits):
#     #     token_logits[]
#     return token_logits
