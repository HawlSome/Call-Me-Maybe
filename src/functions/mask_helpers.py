#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   mask_helpers.py                                      :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 22:30:13 by varandri            #+#    #+#            #
#   Updated: 2026/10/05 21:12:24 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import Any
import numpy as np
import numpy.typing as npt


def get_options(*, caller: Any) -> npt.NDArray[np.int64] | None:
    from classes import Types, States
    from functions import get_function_names

    model = caller.model
    state = caller.transition_state.state
    allowed_options = np.array([], dtype=np.int64)
    if state == States.NAME:
        func_names = get_function_names(caller.func_definitions)
        allowed_options = np.array(
            sorted({
                token for name in func_names
                for token in model.encode_to_int(name)
            }),
            dtype=np.int64
        )
    if state == States.PARAMS:
        if not caller.transition_state.parameter_key:
            return None
        _, k_type = caller.transition_state.parameter_key
        if k_type in {Types.INT, Types.FLOAT}:
            number_str = '-".,0123456789'
            allowed_options = np.array(
                sorted({
                    token for ch in number_str
                    for token in model.encode_to_int(ch)
                }),
                dtype=np.int64
            )
        elif k_type == Types.BOOLEAN:
            bool_str = ["true", "false"]
            allowed_options = np.array(
                sorted({
                    token for boolean in bool_str
                    for token in model.encode_to_int(boolean)
                }),
                dtype=np.int64
            )
        elif k_type == Types.STRING:
            vocab_size = model.get_vocab_size()
            allowed: list[int] = []
            for token in range(vocab_size):
                decoded_token = model.decode(token)
                if len(decoded_token) > 1 and '"' in decoded_token:
                    continue
                allowed.append(token)
            allowed_options = np.array(allowed, dtype=np.int64)
    return allowed_options
