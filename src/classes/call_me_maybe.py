#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   call_me_maybe.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:20:32 by varandri            #+#    #+#            #
#   Updated: 2026/10/05 21:11:34 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    # from .enums import States, Types
    from pydantic import BaseModel
    # from pydantic import Field, ConfigDict, model_validator
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


class CallMeMaybe(BaseModel):
    pass
