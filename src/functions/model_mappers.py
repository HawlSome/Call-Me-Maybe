#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   model_mappers.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:29:07 by varandri            #+#    #+#            #
#   Updated: 2026/10/05 11:44:46 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from ..classes import FunctionDefinition
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


def get_function_names(func_defs: list[FunctionDefinition]) -> list[str]:
    return [
        f'"{func.name}"' for func in func_defs
    ]
