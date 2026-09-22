#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   enums.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/19 19:51:21 by varandri            #+#    #+#            #
#   Updated: 2026/09/22 12:38:44 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from enum import Enum


class States(Enum):
    NAME = "name"
    PARAMS = "params"


class Types(Enum):
    STRING = "string"
    NUMBER = "number"
    INT = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    NULL = ""
