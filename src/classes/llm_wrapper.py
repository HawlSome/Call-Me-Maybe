#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   llm_wrapper.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:31:12 by varandri            #+#    #+#            #
#   Updated: 2026/10/14 13:22:16 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Provide a typed interface to the language model used by the project."""

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
    """Wrap language-model tokenization and token-selection operations.

    Attributes:
        model: Underlying language model used for encoding and inference.
    """

    model: Small_LLM_Model = Field(default=Small_LLM_Model())
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __get_logits(self, tokens: list[int]) -> list[float]:
        """Return the model logits for the supplied token sequence.

        Args:
            tokens: Token IDs provided as model input.

        Returns:
            The model's logits for the input sequence.
        """
        return cast(list[float], self.model.get_logits_from_input_ids(tokens))

    def encode_to_int(self, string: str) -> list[int]:
        """Encode text as a list of token IDs.

        Args:
            string: Text to encode.

        Returns:
            Token IDs corresponding to the input text.
        """
        encoded_str: list[int] = []
        for token in self.model.encode(string)[0]:
            encoded_str.append(token)
        return encoded_str

    def decode(self, tokens: list[int]) -> str:
        """Decode token IDs into text.

        Args:
            tokens: Token IDs to decode.

        Returns:
            The decoded text.
        """
        return str(self.model.decode(tokens))

    def get_vocab_size(self) -> int:
        """Return the number of entries in the model vocabulary.

        Returns:
            The number of vocabulary entries.
        """
        vocab_file = Path(self.model.get_path_to_vocab_file())
        with vocab_file.open(mode="r") as file:
            vocabs = load(file)
        return len(vocabs)

    def get_best_token(
        self, *, prompt: list[int], options: Any
    ) -> int:
        """Select the highest-logit token from the allowed options.

        Args:
            prompt: Token IDs used to obtain model logits.
            options: Indices of logits eligible for selection.

        Returns:
            The token ID with the highest logit among the options.
        """
        logits = self.__get_logits(prompt)
        np_logits = np.array(logits, dtype=np.float32)
        masked_logits = np.full_like(np_logits, -np.inf)
        masked_logits[options] = np_logits[options]
        return int(np.argmax(masked_logits))
