#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   helpers.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/08 18:47:23 by varandri            #+#    #+#            #
#   Updated: 2026/10/11 01:54:54 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Helper functions for decoding generated function parameters."""

from ..classes import Types


def parameter_ending(
    max_token: int, parameter: str,
    decoded_token: str, k_type: Types
) -> bool:
    """Determine whether the current parameter value is complete.

    Args:
        max_token: Remaining token limit for generating the value.
        parameter: Value text generated so far.
        decoded_token: Next decoded token to consider.
        k_type: Expected type of the parameter.

    Returns:
        Whether generation should stop for the current parameter.
    """
    next_word = parameter + decoded_token
    return (
        max_token <= 0 or
        (
            k_type == Types.STRING and
            len(parameter) > 1 and
            next_word.count('"') >= 2
        ) or
        (
            k_type == Types.BOOLEAN and
            parameter in ["true", "false"]
        ) or
        (
            k_type in [Types.INT, Types.FLOAT] and
            "," in next_word
        ) or
        (
            k_type == Types.INT and
            "." in next_word
        )
    )
