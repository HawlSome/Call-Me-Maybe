# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   parsing.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 14:15:04 by varandri            #+#    #+#            #
#   Updated: 2026/09/15 20:14:04 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import argparse
from json import load
from ..classes import Function_calling, Function_definition


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


def __store_prompts(
    raw_promts: list[dict[str, str | dict[str, str | dict[str, str]]]]
) -> list[Function_calling]:
    prompts: list[Function_calling] = []
    for p in raw_promts:
        prompts.append(
            Function_calling(
                prompt=p["prompt"]
            )
        )
    return prompts


def __srote_function_defs(
    raw_fd: list[dict[str, str | dict[str, str | dict[str, str]]]]
) -> list[Function_definition]:
    definitions: list[Function_definition] = []

    for fd in raw_fd:
        definitions.append(
            Function_definition(
                name=fd["name"],
                description=fd["description"],
                parameters=fd["parameters"],
                returns=fd["returns"]
            )
        )
        # print(fd["description"])
    return definitions


def parse_args() -> tuple[
    list[Function_calling], list[Function_definition], str
]:
    func_def, input_file, output_file = __parse()
    input_content, func_def_content = (
        __get_json(input_file),
        __get_json(func_def)
    )
    prompts = __store_prompts(input_content)
    definitions = __srote_function_defs(func_def_content)
    return (prompts, definitions, output_file)
