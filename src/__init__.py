# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 15:09:25 by varandri            #+#    #+#            #
#   Updated: 2026/09/28 13:09:21 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from . import functions, classes
except (ModuleNotFoundError, KeyboardInterrupt) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}.")
    exit()


__all__ = [
    'functions', 'classes'
]
