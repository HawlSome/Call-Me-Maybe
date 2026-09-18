# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   parsing.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 14:15:04 by varandri            #+#    #+#            #
#   Updated: 2026/09/18 17:25:46 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import Any
import argparse
from json import load
from ..classes import (
    Function_Parameters,
    Function_Calling, Function_Definition
)
from typing import cast


def __parse() -> tuple[str, ...]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json"
    )
    parser.add_argument(
        "--input",
        default="data/input/function_calling_tests.json"
    )
    parser.add_argument(
        "--output",
        default="data/output/function_calls.json"
    )
    args = parser.parse_args()
    return (args.functions_definition, args.input, args.output)


def __get_json(file_name: str) -> list[
    dict[str, str | dict[str, str | dict[str, str]]]
]:
    func_def: list[
        dict[str, str | dict[str, str | dict[str, str]]]
    ] = []
    with open(file_name, "r") as file:
        func_def = load(file)
    return func_def


def __store_prompts(raw_promts: Any) -> list[Function_Calling]:
    prompts: list[Function_Calling] = []
    for p in raw_promts:
        prompts.append(
            Function_Calling(
                prompt=str(p["prompt"])
            )
        )
    return prompts


def __srote_function_defs(raw_fd: Any) -> list[Function_Definition]:
    definitions: list[Function_Definition] = []

    for fd in raw_fd:
        name: str = str(fd["name"])
        description: str = str(fd["description"])
        parameters: list[Function_Parameters] = [
            Function_Parameters(
                key=k,
                value=v
            )
            for k, v in zip(
                fd['parameters'].keys(),
                fd['parameters'].values()
            )
        ]
        returns: dict[str, str] = cast(
            dict[str, str], fd["returns"]
        )
        definitions.append(
            Function_Definition(
                name=name,
                description=description,
                parameters=parameters,
                returns=returns
            )
        )
    return definitions


def parse_args() -> tuple[
    list[Function_Calling], list[Function_Definition], str
]:
    func_def, input_file, output_file = __parse()
    input_content, func_def_content = (
        __get_json(input_file),
        __get_json(func_def)
    )
    prompts = __store_prompts(input_content)
    definitions = __srote_function_defs(func_def_content)
    return (prompts, definitions, output_file)
