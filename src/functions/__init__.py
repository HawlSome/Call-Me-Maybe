#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 14:18:26 by varandri            #+#    #+#            #
#   Updated: 2026/10/05 11:45:24 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Public exports for the functions package.

This module exposes the parsing and helper utilities used by the decoding
pipeline.
"""

try:
    from .parser import parse_args, store_JSON
    from .model_mappers import get_function_names
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
    'parse_args', 'store_JSON',
    'get_function_names'
    # 'get_func_def_names', 'get_func_defs', 'get_func_parameters',
    # 'get_func_struct',
    # 'set_state_type', 'get_keys', 'is_ending_token',
    # 'get_next_parameter', 'smart_strip', 'smart_cast',
    # 'is_ending_parameters'
]
