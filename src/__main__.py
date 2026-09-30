#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/14 10:11:43 by varandri            #+#    #+#            #
#   Updated: 2026/09/30 13:17:29 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from .functions import parse_args
    from pydantic import ValidationError
    from .classes import Decoder
    from json import JSONDecodeError
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


def main() -> None:
    try:
        prompts, fn_defs, output = parse_args()
        decoder = Decoder(
            function_definitions=fn_defs,
            function_callings=prompts
        )
        decoder.get_fun_calls(path_outdir=output)
    except KeyboardInterrupt as err:
        print(
            f"\n[ERROR] - {err.__class__.__name__}: "
            "the program has stopped unexpectedly."
        )
    except KeyError as err:
        print(
            f"\n[ERROR] - {err.__class__.__name__}: "
            f"{err} not found."
        )
    except (
        FileExistsError, FileNotFoundError, PermissionError,
        IsADirectoryError
    ) as err:
        print(
            f"\n[ERROR] - {err.__class__.__name__} - "
            f"{err} not found."
        )
    except JSONDecodeError as err:
        print(
            f"\n[ERROR] - {err.__class__.__name__}: "
            f"{err}."
        )
    except ValidationError as e:
        print(f"\n[ERROR] - {e.__class__.__name__}:")
        for error in e.errors():
            msg: str | None = error.get("msg")
            print(f"- {msg}")


if __name__ == "__main__":
    main()
