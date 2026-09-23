#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/14 10:11:43 by varandri            #+#    #+#            #
#   Updated: 2026/09/23 15:38:15 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from .functions import parse_args
    from pydantic import ValidationError
    from .classes import Decoder
except (ModuleNotFoundError, ImportError) as e:
    print(f"[ERROR]: {e}")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"[ERROR] {e.__class__.__name__}: Program has stopped."
    )
    exit()


def main() -> None:
    try:
        prompts, fn_defs, output = parse_args()
        decoder = Decoder(
            function_definitions=fn_defs,
            function_callings=prompts
        )
        decoder.show_funcs()
    except KeyboardInterrupt as err:
        print(f"[ERROR]: {err.__class__.__name__}: the program has stopped.")
    except ValidationError as e:
        print("Expected validation error:")
        for error in e.errors():
            msg: str | None = error.get("msg")
            print(f"{msg}")


if __name__ == "__main__":
    print()
    main()
