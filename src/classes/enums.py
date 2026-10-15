#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   enums.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/19 19:51:21 by varandri            #+#    #+#            #
#   Updated: 2026/10/15 16:52:57 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Enum definitions used by the decoding pipeline.

These enumerations describe the decoder states and supported parameter
types.
"""

from enum import Enum


class States(Enum):
    """Stages of function-call decoding.

    Attributes:
        NAME: The decoder is selecting a function name.
        PARAMS: The decoder is retrieving function parameters.
    """

    NAME = "name"
    PARAMS = "params"


class Types(Enum):
    """Parameter value types supported by the decoder.

    Attributes:
        STRING: A string parameter.
        INT: An integer parameter.
        FLOAT: A floating-point parameter.
        BOOLEAN: A boolean parameter.
    """

    STRING = "string"
    INT = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
