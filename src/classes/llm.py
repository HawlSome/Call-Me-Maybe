#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   llm.py                                               :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/22 20:56:47 by varandri            #+#    #+#            #
#   Updated: 2026/09/24 13:48:21 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import cast, TYPE_CHECKING
    from .enums import States, Types
    from llm_sdk import Small_LLM_Model  # type: ignore
    from pydantic import BaseModel, Field, ConfigDict
    from numpy import argmax
except ModuleNotFoundError:
    raise ModuleNotFoundError

if TYPE_CHECKING:
    from .decoder import Decoder


class Llm(BaseModel):
    model: Small_LLM_Model = Field(
        default=Small_LLM_Model()
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def int_encode(self, string: str) -> list[int]:
        encoded: list[int] = []
        for token in self.model.encode(string)[0]:
            encoded.append(int(token))
        return encoded

    def decode(self, tokens: list[int]) -> str:
        return str(self.model.decode(tokens))

    def __get_logits(self, tokens: list[int]) -> list[float]:
        return cast(
            list[float],
            self.model.get_logits_from_input_ids(list(tokens))
        )

    def get_best_token(
            self, decoder: "Decoder", encoded_prompt: list[int]
    ) -> int:
        from ..functions import (get_func_def_names)

        def mask_logits(logits: list[float]) -> list[float]:
            def get_encoded_func_def_names() -> list[list[int]]:
                encoded_names: list[list[int]] = []
                for name in get_func_def_names(
                    decoder.function_definitions
                ):
                    encoded_names.append(
                        self.int_encode(name)
                    )
                return encoded_names

            def get_encoded_numeric_mask() -> list[int]:
                encoded_numeric_mask: list[int] = []
                for ch in '-".,0123456789':
                    encoded_numeric_mask.extend(self.int_encode(ch))
                return encoded_numeric_mask

            def get_encoded_str_mask() -> list[int]:
                encoded_str_mask: list[int] = []
                for ch in '\"':
                    encoded_str_mask.extend(self.int_encode(ch))
                return encoded_str_mask

            def get_encoded_boolen_mask() -> list[list[int]]:
                encoded_bool_mask: list[list[int]] = []
                for boolean in ["true", "false", '"', "}", ","]:
                    encoded_bool_mask.append(self.int_encode(boolean))
                return encoded_bool_mask

            masked_logits = [float("-inf") for _ in logits]
            if decoder.state.state == States.NAME:
                for enc_names in get_encoded_func_def_names():
                    for token in enc_names:
                        masked_logits[token] = logits[token]
            if decoder.state.state == States.PARAMS:
                if (
                    decoder.state.type == Types.NUMBER or
                    decoder.state.type == Types.INT or
                    decoder.state.type == Types.FLOAT
                ):
                    for token in get_encoded_numeric_mask():
                        masked_logits[token] = logits[token]
                if decoder.state.type == Types.STRING:
                    for token in get_encoded_str_mask():
                        logits[token] = float("-inf")
                        masked_logits = logits
                if decoder.state.type == Types.BOOLEAN:
                    for bool_values in get_encoded_boolen_mask():
                        for token in bool_values:
                            masked_logits[token] = logits[token]
            return masked_logits

        logits = self.__get_logits(encoded_prompt)
        masked_logits = mask_logits(logits)
        return int(argmax(masked_logits))
