#!/usr/bin/env python3
# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   parser.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 14:15:04 by varandri            #+#    #+#            #
#   Updated: 2026/10/12 18:43:49 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Input parsing utilities.

This module loads the project data files and converts them into the
Pydantic models used by the decoder pipeline.
"""

try:
    from typing import Any
    import argparse
    from json import load
    from json import dump
    from pathlib import Path
    from pydantic import ValidationError
    from ..classes import (
        FunctionCalling, FunctionDefinition
    )
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


def __parse() -> tuple[str, ...]:
    """Parse the CLI arguments for the project.

    Returns:
        A tuple containing the function-definition path, input path, and
        output path.
    """
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
    """Load a JSON file and return its parsed content.

    Args:
        file_name: Path to the JSON file to read.

    Returns:
        The parsed JSON payload.
    """
    func_def: list[
        dict[str, str | dict[str, str | dict[str, str]]]
    ] = []
    file_path: Path = Path(file_name)
    with file_path.open(mode="r") as file:
        func_def = load(file)
    return func_def


def __store_function_callings(raw_promts: Any) -> list[FunctionCalling]:
    """Convert raw prompt payloads into validated model objects.

    Args:
        raw_promts: Prompt data loaded from JSON.

    Returns:
        A list of validated ``FunctionCalling`` objects.
    """
    prompts: list[FunctionCalling] = []
    for p in raw_promts:
        try:
            prompts.append(
                FunctionCalling.model_validate(p)
            )
        except ValidationError as e:
            print(f"\n[ERROR] - {e.__class__.__name__}:")
            for error in e.errors():
                loc: str | None = error.get("loc")
                msg: str | None = error.get("msg")
                if loc:
                    print(f"- {loc[0]}: {msg}")
                else:
                    print(f"- {msg}")
                continue
    return prompts


def __srote_function_defs(raw_fd: Any) -> list[FunctionDefinition]:
    """Convert raw function-definition data into validated model objects.

    Args:
        raw_fd: Function-definition data loaded from JSON.

    Returns:
        A list of validated ``FunctionDefinition`` objects.
    """
    definitions: list[FunctionDefinition] = []

    for fd in raw_fd:
        try:
            definitions.append(
                FunctionDefinition.model_validate(fd)
            )
        except ValidationError as e:
            print(f"\n[ERROR] - {e.__class__.__name__}:")
            for error in e.errors():
                loc: str | None = error.get("loc")
                msg: str | None = error.get("msg")
                if loc:
                    print(f"- {loc[0]}: {msg}")
                else:
                    print(f"- {msg}")
                continue
    return definitions


def parse_args() -> tuple[
    list[FunctionCalling], list[FunctionDefinition], str
]:
    """Parse command-line arguments and return loaded project data.

    Returns:
        A tuple containing the prompts, definitions, and output path.
    """
    func_def, input_file, output_file = __parse()
    input_content, func_def_content = (
        __get_json(input_file),
        __get_json(func_def)
    )
    prompts = __store_function_callings(input_content)
    definitions = __srote_function_defs(func_def_content)
    return (prompts, definitions, output_file)


def store_JSON(json_content: list[dict[str, Any]], path_output: str) -> None:
    """Write JSON content to the output path.

    Args:
        json_content: Data to serialize.
        path_output: Output file path.
    """
    path: Path = Path(path_output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode="w") as file:
        dump(json_content, file, indent=4)
