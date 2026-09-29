#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   parsing.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 14:15:04 by varandri            #+#    #+#            #
#   Updated: 2026/09/29 11:58:20 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any
    import argparse
    from json import load
    from ..classes import (
        FunctionParameters,
        FunctionCalling, FunctionDefinition
    )
except (ModuleNotFoundError, KeyboardInterrupt) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}.")
    exit()


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
        # print(p)
        prompts.append(
            FunctionCalling.model_validate(p)
        )
    return prompts


def __srote_function_defs(raw_fd: Any) -> list[FunctionDefinition]:
    definitions: list[FunctionDefinition] = []

    for fd in raw_fd:
        parameters: list[FunctionParameters] | None = []
        fd_params: Any = fd["parameters"]
        if not fd_params:
            parameters = None
        try:
            for k, v in zip(
                fd_params.keys(),
                fd_params.values()
            ):
                if parameters is not None:
                    parameters.append(
                        FunctionParameters(
                            key=k,
                            value=v
                        )
                    )
            fd["parameters"] = parameters
        except Exception:
            pass
        definitions.append(
            FunctionDefinition.model_validate(fd)
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
