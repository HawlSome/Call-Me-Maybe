# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   tokens.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 22:41:53 by varandri            #+#    #+#            #
#   Updated: 2026/09/15 23:17:42 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

def mask_logits(
    logits: list[float], encoded_fn_def: list[list[int]]
) -> list[float]:
    masked_logits: list[float] = [float("-inf") for _ in logits]
    for fn_def in encoded_fn_def:
        for i in fn_def:
            masked_logits[i] = logits[i]
    return masked_logits


def get_best_token(masked_logits: list[float]) -> dict[int, float]:
    best_tokens: dict[int, float] = {
        i: masked_logits[i] for i in range(len(masked_logits))
        if masked_logits[i] > 0
    }
    return best_tokens
