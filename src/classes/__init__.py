#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 19:27:45 by varandri            #+#    #+#            #
#   Updated: 2026/10/07 22:39:08 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Public exports for the classes package.

This module exposes the model types and decoder entry point used across the
project.
"""

try:
    from .models import (
        FunctionCalling, FunctionDefinition
    )
    from .enums import Types, States
    from .call_me_maybe import CallMeMaybe
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


__all__ = [
    'FunctionCalling', 'FunctionDefinition',
    'Types', 'States',
    'CallMeMaybe'
]
