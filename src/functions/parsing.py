#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   parsing.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 14:15:04 by varandri            #+#    #+#            #
#   Updated: 2026/09/19 19:49:29 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import Any
import argparse
from json import load
from ..classes import (
    FunctionParameters,
    FunctionCalling, FunctionDefinition
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


def __store_prompts(raw_promts: Any) -> list[FunctionCalling]:
    prompts: list[FunctionCalling] = []
    for p in raw_promts:
        prompts.append(
            FunctionCalling(
                prompt=str(p["prompt"])
            )
        )
    return prompts


def __srote_function_defs(raw_fd: Any) -> list[FunctionDefinition]:
    definitions: list[FunctionDefinition] = []

    for fd in raw_fd:
        name: str = str(fd["name"])
        description: str = str(fd["description"])
        parameters: list[FunctionParameters] = [
            FunctionParameters(
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
            FunctionDefinition(
                name=name,
                description=description,
                parameters=parameters,
                returns=returns
            )
        )
    return definitions


def parse_args() -> tuple[
    list[FunctionCalling], list[FunctionDefinition], str
]:
    func_def, input_file, output_file = __parse()
    input_content, func_def_content = (
        __get_json(input_file),
        __get_json(func_def)
    )
    prompts = __store_prompts(input_content)
    definitions = __srote_function_defs(func_def_content)
    return (prompts, definitions, output_file)
