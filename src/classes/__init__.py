#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 19:27:45 by varandri            #+#    #+#            #
#   Updated: 2026/09/28 13:09:21 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from .models import (
        FunctionParameters,
        FunctionCalling, FunctionDefinition
    )
    from .decoder import Decoder
except (ModuleNotFoundError, KeyboardInterrupt) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}.")
    exit()


__all__ = [
    'FunctionParameters',
    'FunctionCalling', 'FunctionDefinition',
    'Decoder'
]
