#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   enums.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/19 19:51:21 by varandri            #+#    #+#            #
#   Updated: 2026/09/30 13:44:23 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Enum definitions used by the decoding pipeline.

These enumerations describe the decoder states and supported parameter
types.
"""

from enum import Enum


class States(Enum):
    """Runtime states used during decoding."""

    NAME = "name"
    PARAMS = "params"


class Types(Enum):
    """Supported parameter types for decoded values."""

    STRING = "string"
    NUMBER = "number"
    INT = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    NULL = ""
