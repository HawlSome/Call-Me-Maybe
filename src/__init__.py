#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 15:09:25 by varandri            #+#    #+#            #
#   Updated: 2026/09/30 13:52:40 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Project package initialization.

This package exposes the application submodules used by the command-line
entry point and the decoder pipeline.
"""

try:
    from . import functions, classes
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
    'functions', 'classes'
]
