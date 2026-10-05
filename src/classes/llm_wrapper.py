#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   llm_wrapper.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:31:12 by varandri            #+#    #+#            #
#   Updated: 2026/10/05 21:18:50 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from pathlib import Path
    from typing import cast, Any
    from json import load
    import numpy as np
    from llm_sdk import Small_LLM_Model  # type: ignore
    from pydantic import BaseModel, ConfigDict, Field
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
    model: Small_LLM_Model = Field(default=Small_LLM_Model())
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __get_logits(self, tokens: list[int]) -> list[float]:
        return cast(list[float], self.model.get_logits_from_input_ids(tokens))

    def encode_to_int(self, string: str) -> list[int]:
        encoded_str: list[int] = []
        for token in self.model.encode(string)[0]:
            encoded_str.append(token)
        return encoded_str

    def decode(self, tokens: list[int]) -> str:
        return str(self.model.decode(tokens))

    def get_vocab_size(self) -> int:
        vocab_file = Path(self.model.get_path_to_vocab_file())
        with vocab_file.open(mode="r") as file:
            vocabs = load(file)
        return len(vocabs)

    def get_best_token(
        self, *, prompt: list[int], options: Any
    ) -> int:
        logits = self.__get_logits(prompt)
        np_logits = np.array(logits, dtype=np.float32)
        masked_logits = np.full_like(np_logits, -np.inf)
        masked_logits[options] = np_logits[options]
        return int(np.argmax(masked_logits))
