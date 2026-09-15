# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/14 10:11:43 by varandri            #+#    #+#            #
#   Updated: 2026/09/15 23:57:50 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from llm_sdk import Small_LLM_Model  # type: ignore
    from .functions import (
        encode_fn_def_name,
        parse_args, encode_fn_def, encode_prompts, mask_logits, get_best_token
    )
    from pydantic import ValidationError
    from numpy import argmax
except (ModuleNotFoundError, ImportError) as e:
    print(f"[ERROR]: {e}")
    exit()


def main() -> None:
    try:
        prompts, fn_defs, output = parse_args()
        model = Small_LLM_Model()
        encoded_fn_def: list[list[int]] = []
        encoded_fn_def_name: list[list[int]] = []
        encoded_prompts: list[list[int]] = []
        encode_fn_def(model, fn_defs, encoded_fn_def)
        encode_prompts(model, prompts, encoded_prompts)
        encode_fn_def_name(model, fn_defs, encoded_fn_def_name)
        # logits = model.get_logits_from_input_ids(int_encoder(model, "add_number"))
        # masked_logits = mask_logits(logits, encoded_fn_def_name)
        # # bese_tokens = get_best_token(masked_logits)
        # # print(max(bese_tokens, key=lambda x: bese_tokens[x]))
        # print(model.decode(argmax(masked_logits)))

    except ValidationError as e:
        print("Expected validation error:")
        for error in e.errors():
            msg: str | None = error.get("msg")
            print(f"{msg}")


if __name__ == "__main__":
    main()
