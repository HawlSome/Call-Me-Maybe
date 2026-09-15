# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   tokens.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 22:41:53 by varandri            #+#    #+#            #
#   Updated: 2026/09/16 01:01:48 by varandri           ###   ########.fr      #
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
