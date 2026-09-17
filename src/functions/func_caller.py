# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   func_caller.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/16 00:09:28 by varandri            #+#    #+#            #
#   Updated: 2026/09/17 14:59:45 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from llm_sdk import Small_LLM_Model  # type: ignore
from ..classes import Function_definition, Function_calling
from ..functions import (
    int_encoder, encode_fn_def_name, encode_fn_struct, mask_logits,
)
from numpy import argmax


def __get_func_def_dict(
    func_def: list[Function_definition]
) -> list[dict[str, str]]:
    func_def_dict: list[dict[str, str]] = []
    for fd in func_def:
        name = fd.name
        info = fd.description
        parameters = fd.parameters
        returns = fd.returns
        func_def_dict.append(
            {
                "name": name,
                "description": info,
                "parameters": str(parameters),
                "returns": str(returns)
            }
        )
    return func_def_dict


def get_func_name(
    model: Small_LLM_Model,
    prompt: str, fn_defs: list[Function_definition]
) -> str:
    func_def_dict = __get_func_def_dict(fn_defs)
    raw_prompt: str = (
        "You are a function selector. "
        "You will select a function name from a function definitions list. "
        "You will chose a name that correspond to a given question. "
        f'Question: "{prompt}". '
        f"functions definition: {func_def_dict} ."
        'Found name: {"name": "'
    )
    func_name: str = ""
    encoded_prompt: list[int] = int_encoder(model, raw_prompt)
    encoded_fn_def_name: list[list[int]] = []
    encode_fn_def_name(model, fn_defs, encoded_fn_def_name)
    while True:
        raw_logits: list[float] = (
            model.get_logits_from_input_ids(encoded_prompt)
        )
        masked_logits: list[float] = (
            mask_logits(raw_logits, encoded_fn_def_name)
        )
        best_token: int = int(argmax(masked_logits))
        if '"' in model.decode(best_token):
            break
        func_name += model.decode(best_token)
        encoded_prompt.append(best_token)
    return func_name


def __get_key_type(
    param_struct: dict[str, dict[str, str]], key: str
) -> str:
    return param_struct[key]["type"]


def __get_numeric_mask(model: Small_LLM_Model) -> list[list[int]]:
    numeric_mask: list[list[int]] = []
    values: str = '0123456789-.,"'
    numeric_mask.append(int_encoder(model, values))
    return numeric_mask


def get_parameters(
    model: Small_LLM_Model, func_name: str,
    prompt: str, fn_defs: list[Function_definition]
) -> str:
    func_def: Function_definition = [
        fn_def for fn_def in fn_defs if fn_def.name == func_name
    ][0]
    parameters_struct: dict[str, dict[str, str]] = func_def.parameters
    parameters_keys: list[str] = list(parameters_struct.keys())

    i = 0
    encoded_fn_struct: list[int] = []
    parameters: str = "{"

    encode_fn_struct(model, func_name, fn_defs, encoded_fn_struct)
    raw_prompt: str = (
        "You are a parameters mapper. "
        "You will have a function definition to take reference on. "
        "You will also have a prompt to get the value from. "
        'The format of the parameters should be like {"a": "222", "b": "222" ...}'
        f"Function definition: {model.decode(encoded_fn_struct)} ."
        f"Prompt: {prompt} ."
        f"Answer: "
    )
    parameters += f'{parameters_keys[0]}: "'
    encoded_raw_prompt: list[int] = int_encoder(model, raw_prompt)
    encoded_raw_prompt.extend(int_encoder(model, parameters))
    encoded_prompt: list[int] = int_encoder(model, prompt)
    masked_logits: list[float] = []
    while True:
        if i >= len(parameters_keys):
            parameters += "}"
            break
        raw_logits: list[float] = (
            model.get_logits_from_input_ids(encoded_raw_prompt)
        )
        if (
            __get_key_type(parameters_struct, parameters_keys[i]).lower()
            in "number"
        ):
            masked_logits = (
                mask_logits(raw_logits, __get_numeric_mask(model))
            )
        if (
            __get_key_type(parameters_struct, parameters_keys[i]).lower()
            in "strings"
        ):
            masked_logits = (
                mask_logits(raw_logits, [encoded_prompt])
            )
        best_token: int = int(argmax(masked_logits))
        if (model.decode(best_token) in '",.'):
            break
        parameters += model.decode(best_token)
        encoded_raw_prompt.extend(int_encoder(model, parameters))
        # i += 1
        # if i < len(parameters_keys):
        #     parameters += f"{model.decode(best_token)}, {parameters_keys[i]}: "
        #     encoded_raw_prompt.extend(int_encoder(model, parameters))
        # else:
        #     parameters += model.decode(best_token)
    return parameters


def function_calling(
    model: Small_LLM_Model, prompts: list[Function_calling],
    fn_defs: list[Function_definition]
) -> list[dict[str, str | dict[str, str]]]:
    call_them_maybe: list[dict[str, str | dict[str, str]]] = []
    return call_them_maybe
