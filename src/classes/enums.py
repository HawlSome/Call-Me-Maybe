#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   enums.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/19 19:51:21 by varandri            #+#    #+#            #
#   Updated: 2026/09/19 19:58:21 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from enum import Enum


class States(Enum):
    NAME = "name"
    PARAMS = "params"


class Types(Enum):
    STRING = "string"
    NUMBER = "number"
    NULL = ""
