#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   llm_wrapper.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:31:12 by varandri            #+#    #+#            #
#   Updated: 2026/10/05 11:36:42 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from .enums import States, Types
    from pydantic import BaseModel, Field, ConfigDict, model_validator
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


class Llm(BaseModel):
    pass
