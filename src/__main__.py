# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/14 10:11:43 by varandri            #+#    #+#            #
#   Updated: 2026/09/16 01:24:11 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from llm_sdk import Small_LLM_Model  # type: ignore
    from .functions import parse_args, get_func_name
    from pydantic import ValidationError
except (ModuleNotFoundError, ImportError) as e:
    print(f"[ERROR]: {e}")
    exit()


def main() -> None:
    try:
        prompts, fn_defs, output = parse_args()
        model = Small_LLM_Model()
        # print(prompts[0].prompt)
        print(get_func_name(
            model, prompts[0].prompt, fn_defs
        ))

    except ValidationError as e:
        print("Expected validation error:")
        for error in e.errors():
            msg: str | None = error.get("msg")
            print(f"{msg}")


if __name__ == "__main__":
    print()
    main()
