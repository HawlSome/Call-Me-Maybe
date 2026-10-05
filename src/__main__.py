#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/14 10:11:43 by varandri            #+#    #+#            #
#   Updated: 2026/10/05 21:10:33 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Command-line entry point for the project.

This module parses the runtime arguments and starts the decoding pipeline
used to generate function calls from the provided prompts.
"""

try:
    from .functions import parse_args, get_function_parameters_keys
    from pydantic import ValidationError
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
    """Run the command-line application.

    Returns:
        None. The decoded function calls are printed and persisted to disk.
    """
    prompts, fn_defs, output = parse_args()
    print(get_function_parameters_keys(fn_defs, "fn_add_numbers"))
    print()
    # decoder = Decoder(
    #     function_definitions=fn_defs,
    #     function_callings=prompts
    # )
    # decoder.get_fun_calls(path_outdir=output)


if __name__ == "__main__":
    try:
        main()
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
    except (ModuleNotFoundError, ImportError) as e:
        print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    except (ValueError, TypeError) as e:
        print(f"\n[ERROR] - {e.__class__.__name__}: Invalid value Type.")
