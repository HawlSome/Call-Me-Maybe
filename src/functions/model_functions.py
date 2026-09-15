# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   model_functions.py                                   :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 15:59:16 by varandri            #+#    #+#            #
#   Updated: 2026/09/15 20:17:08 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from llm_sdk import Small_LLM_Model  # type: ignore


def int_encoder(model: Small_LLM_Model, string: str) -> list[int]:
    encoded: list[int] = []
    for token in model.encode(string)[0]:
        encoded.append(int(token))
    return encoded


def get_token_logits(
    model: Small_LLM_Model, tokens: list[int]
) -> dict[int, float]:
    token_logits: dict[int, float] = {}
    # logits = model.get_logits_from_input_ids(tokens)
    # for i in len(logits):
    #     token_logits[]
    return token_logits
