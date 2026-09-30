#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 14:18:26 by varandri            #+#    #+#            #
#   Updated: 2026/09/30 13:49:31 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Public exports for the functions package.

This module exposes the parsing and helper utilities used by the decoding
pipeline.
"""

try:
    from .parsing import parse_args, store_JSON
    from .func_def_mappers import (
        get_func_def_names, get_func_defs, get_func_parameters, get_func_struct
    )
    from .param_decoder_helpers import (
        set_state_type, get_keys, clean_answer, is_ending_token,
        get_next_parameter, clean_raw_param, clean_decoded, smart_cast
    )
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
    'get_func_def_names', 'get_func_defs', 'get_func_parameters',
    'get_func_struct',
    'set_state_type', 'get_keys', 'clean_answer', 'is_ending_token',
    'get_next_parameter', 'clean_raw_param', 'clean_decoded', 'smart_cast'
]
