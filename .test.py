#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   model_mappers.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:29:07 by varandri            #+#    #+#            #
#   Updated: 2026/10/08 14:20:00 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any, cast
    from ..classes import FunctionDefinition
    from ..classes import Types
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


def __get_function_parameters(
    func_defs: list[FunctionDefinition], func_name: str
) -> dict[str, dict[str, str]] | None:
    for func in func_defs:
        if func.name == func_name:
            return func.parameters
    return None


def get_function_names(func_defs: list[FunctionDefinition]) -> list[str]:
    return [
        func.name for func in func_defs
    ]


def get_function_struct(
        func_defs: list[FunctionDefinition], func_name: str
) -> dict[str, Any] | None:
    for func in func_defs:
        if func.name == func_name:
            return func.model_dump()
    return None


def get_function_defs_struct(
    func_defs: list[FunctionDefinition]
) -> list[dict[str, Any]]:
    return cast(
        list[dict[str, Any]],
        [
            get_function_struct(func_defs, func_name)
            for func_name in get_function_names(func_defs)
        ]
    )


def get_function_parameters_keys(
    func_defs: list[FunctionDefinition], func_name: str
) -> list[tuple[str, Types]] | None:
    func_parameters = __get_function_parameters(func_defs, func_name)
    function_keys: list[tuple[str, Types]] = []
    if not func_parameters:
        return None
    for key in func_parameters.keys():
        raw_type: str = func_parameters[key]["type"].lower()
        enum_type: Types
        if raw_type in "strings":
            enum_type = Types.STRING
        elif raw_type in "booleans":
            enum_type = Types.BOOLEAN
        elif raw_type in "integers":
            enum_type = Types.INT
        elif raw_type in "numbers" or raw_type in "floats":
            enum_type = Types.FLOAT
        else:
            enum_type = Types.STRING
        function_keys.append((key, enum_type))
    return function_keys
#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   helpers.py                                           :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/08 18:47:23 by varandri            #+#    #+#            #
#   Updated: 2026/10/11 01:54:54 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from ..classes import Types


def parameter_ending(
    max_token: int, parameter: str,
    decoded_token: str, k_type: Types
) -> bool:
    next_word = parameter + decoded_token
    return (
        max_token <= 0 or
        (
            k_type == Types.STRING and
            len(parameter) > 1 and
            next_word.count('"') >= 2
        ) or
        (
            k_type == Types.BOOLEAN and
            parameter in ["true", "false"]
        ) or
        (
            k_type in [Types.INT, Types.FLOAT] and
            "," in next_word
        ) or
        (
            k_type == Types.INT and
            "." in next_word
        )
    )
#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 14:18:26 by varandri            #+#    #+#            #
#   Updated: 2026/10/08 19:03:17 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Public exports for the functions package.

This module exposes the parsing and helper utilities used by the decoding
pipeline.
"""

try:
    from .parser import parse_args, store_JSON
    from .model_mappers import (
        get_function_names, get_function_struct, get_function_defs_struct,
        get_function_parameters_keys
    )
    from .mask_helpers import get_options
    from .helpers import parameter_ending
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


__all__ = [
    'parse_args', 'store_JSON',
    'get_function_names', 'get_function_struct', 'get_function_defs_struct',
    'get_function_parameters_keys',
    'get_options',
    'parameter_ending'
]
#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   mask_helpers.py                                      :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 22:30:13 by varandri            #+#    #+#            #
#   Updated: 2026/10/08 21:19:23 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import Any
import numpy as np
import numpy.typing as npt


def get_options(*, caller: Any) -> npt.NDArray[np.int64] | None:
    from ..classes import Types, States
    from ..functions import get_function_names

    model = caller.model
    state = caller.transition_state.state
    allowed_options = np.array([], dtype=np.int64)
    if state == States.NAME:
        func_names = get_function_names(caller.func_defs)
        allowed_options = np.array(
            sorted({
                token for name in func_names
                for token in model.encode_to_int(name)
            }),
            dtype=np.int64
        )
    if state == States.PARAMS:
        if not caller.transition_state.parameter_key:
            return None
        _, k_type = caller.transition_state.parameter_key
        if k_type in {Types.INT, Types.FLOAT}:
            number_str = '-".,0123456789'
            allowed_options = np.array(
                sorted({
                    token for ch in number_str
                    for token in model.encode_to_int(ch)
                }),
                dtype=np.int64
            )
        elif k_type == Types.BOOLEAN:
            bool_str = ["true", "false"]
            allowed_options = np.array(
                sorted({
                    token for boolean in bool_str
                    for token in model.encode_to_int(boolean)
                }),
                dtype=np.int64
            )
        elif k_type == Types.STRING:
            vocab_size = model.get_vocab_size()
            allowed: list[int] = []
            for token in range(vocab_size):
                allowed.append(token)
            allowed_options = np.array(allowed, dtype=np.int64)
    return allowed_options
#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   parser.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 14:15:04 by varandri            #+#    #+#            #
#   Updated: 2026/10/11 01:56:58 by varandri           ###   ########.fr      #
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
        prompts.append(
            FunctionCalling.model_validate(p)
        )
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
        definitions.append(
            FunctionDefinition.model_validate(fd)
        )
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
#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/14 10:11:43 by varandri            #+#    #+#            #
#   Updated: 2026/10/11 02:27:08 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Command-line entry point for the project.

This module parses the runtime arguments and starts the decoding pipeline
used to generate function calls from the provided prompts.
"""

try:
    from .functions import parse_args
    from .classes import CallMeMaybe
    from pydantic import ValidationError
    from json import JSONDecodeError
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


def main() -> None:
    """Run the command-line application.

    Returns:
        None. The decoded function calls are printed and persisted to disk.
    """
    prompts, fn_defs, output = parse_args()
    print()
    caller: CallMeMaybe = CallMeMaybe(
        func_defs=fn_defs,
        func_calls=prompts
    )
    caller.call_functions(path_output=output)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as err:
        print(
            f"\n[ERROR] - {err.__class__.__name__}: "
            "the program has stopped unexpectedly."
        )
    except KeyError as err:
        print(
            f"\n[ERROR] - {err.__class__.__name__}: "
            f"{err} not found."
        )
    except (
        FileExistsError, FileNotFoundError, PermissionError,
        IsADirectoryError
    ) as err:
        print(
            f"\n[ERROR] - {err.__class__.__name__} - "
            f"{err} not found."
        )
    except JSONDecodeError as err:
        print(
            f"\n[ERROR] - {err.__class__.__name__}: "
            f"{err}."
        )
    except ValidationError as e:
        print(f"\n[ERROR] - {e.__class__.__name__}:")
        for error in e.errors():
            msg: str | None = error.get("msg")
            print(f"- {msg}")
    except (ModuleNotFoundError, ImportError) as e:
        print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    except (ValueError, TypeError) as e:
        print(f"\n[ERROR] - {e.__class__.__name__}: Invalid value Type.")
#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   enums.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/19 19:51:21 by varandri            #+#    #+#            #
#   Updated: 2026/10/05 23:22:26 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Enum definitions used by the decoding pipeline.

These enumerations describe the decoder states and supported parameter
types.
"""

from enum import Enum


class States(Enum):
    """Runtime states used during decoding."""

    NAME = "name"
    PARAMS = "params"


class Types(Enum):
    """Supported parameter types for decoded values."""

    STRING = "string"
    INT = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __init__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 19:27:45 by varandri            #+#    #+#            #
#   Updated: 2026/10/07 22:39:08 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Public exports for the classes package.

This module exposes the model types and decoder entry point used across the
project.
"""

try:
    from .models import (
        FunctionCalling, FunctionDefinition
    )
    from .enums import Types, States
    from .call_me_maybe import CallMeMaybe
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


__all__ = [
    'FunctionCalling', 'FunctionDefinition',
    'Types', 'States',
    'CallMeMaybe'
]
#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   llm_wrapper.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:31:12 by varandri            #+#    #+#            #
#   Updated: 2026/10/08 18:04:02 by varandri           ###   ########.fr      #
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
#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   call_me_maybe.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:20:32 by varandri            #+#    #+#            #
#   Updated: 2026/10/11 02:34:12 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any
    from .enums import States, Types
    from pydantic import BaseModel, Field, ConfigDict
    from .models import FunctionCalling, FunctionDefinition, TransitionState
    from .llm_wrapper import Llm
    from json import dumps, loads, JSONDecodeError
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


class CallMeMaybe(BaseModel):
    func_defs: list[FunctionDefinition] = Field(default=...)
    func_calls: list[FunctionCalling] = Field(default=...)
    model: Llm = Field(default=Llm())
    transition_state: TransitionState = Field(default=TransitionState())
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __set_state(
        self, state: States = States.NAME,
        param_keys: tuple[str, Types] | None = None
    ) -> None:
        transition_state: TransitionState = self.transition_state
        transition_state.state = state
        transition_state.parameter_key = param_keys

    def __get_prompt(
        self, call: str, func_defs: list[dict[str, Any]] = [],
        func_name: str = ""
    ) -> str:
        from ..functions import get_function_struct
        transition_state: TransitionState = self.transition_state
        if transition_state.state == States.NAME:
            return (
                "You are a function selector.\n"
                "You will select a function_name from "
                "a list of given function definitions.\n"
                "You will chose the function that match the one "
                "described in a given prompt.\n"
                'the format is as: "name": "fn_function_name".\n'
                f"Function Definitions: {func_defs}. Output:"
                '{'f'"prompt":"{call}", "name": '
            )
        func_struct = get_function_struct(
            func_name=func_name, func_defs=self.func_defs
        )
        return (
            "You are a parameter retriever.\n"
            "You will retrieve the parameters value of a function "
            "in a given prompt. The function structure will also "
            "be given to you for you to take reference on.\n"
            "the value must be a valid JSON value"
            f"Function structure: {func_struct}.\n"
            "{"
            f'"prompt": {dumps(call)}, "name": '
            f'"{func_name}", "parameters":'
        )

    def __call_name(
        self, call: str, func_defs: list[dict[str, Any]],
        func_names: list[str]
    ) -> str:
        from ..functions import get_options
        self.__set_state()
        print(f'Prompt: {dumps(call)}.')
        print("Function Name: ", end="", flush=True)
        model: Llm = self.model
        func_name = ""
        max_token = 20
        name_options = get_options(caller=self)
        prompt = self.__get_prompt(call, func_defs)
        encoded_prompt = model.encode_to_int(prompt)
        while True:
            if (
                max_token <= 0 or
                func_name in func_names
            ):
                break
            best_token = model.get_best_token(
                prompt=encoded_prompt, options=name_options
            )
            decoded_token = model.decode([best_token])
            max_token -= 1
            print(f"{decoded_token}", end="", flush=True)
            func_name += decoded_token
            encoded_prompt.append(best_token)
        self.__set_state(States.PARAMS)
        print()
        return dumps(func_name)

    def __get_current_parameter(self, encoded_prompt: list[int]) -> str:
        from ..functions import get_options, parameter_ending
        transition_state: TransitionState = self.transition_state
        model: Llm = self.model
        parameter: str = ''
        max_token = 100
        if (
            transition_state.parameter_key and
            transition_state.parameter_key[1] in [Types.INT, Types.FLOAT]
        ):
            max_token = 10
        if (
            transition_state.parameter_key and
            transition_state.parameter_key[1] == Types.STRING
        ):
            parameter = '"'
            print('"', end="", flush=True)
        param_option = get_options(caller=self)
        while True:
            best_token = model.get_best_token(
                prompt=encoded_prompt,
                options=param_option
            )
            decoded_token: str = model.decode([best_token])
            max_token -= 1
            if transition_state.parameter_key and parameter_ending(
                max_token, parameter, decoded_token,
                transition_state.parameter_key[1]
            ):
                if (
                    transition_state.parameter_key and
                    transition_state.parameter_key[1] == Types.STRING
                ):
                    decoded_token = decoded_token.split('"')[0] + '"'
                    print(f'{decoded_token}', end="", flush=True)
                    parameter += decoded_token
                encoded_prompt.extend(model.encode_to_int(decoded_token))
                break
            print(f'{decoded_token}', end="", flush=True)
            parameter += decoded_token
            encoded_prompt.append(best_token)
        next = [
            token for ch in ", "
            for token in model.encode_to_int(ch)]
        encoded_prompt.extend(next)
        if (
            transition_state.parameter_key and
            transition_state.parameter_key[1] == Types.FLOAT
        ):
            casted_parameter = str(float(parameter))
            decimal = casted_parameter.replace(parameter, "")
            print(decimal, end="", flush=True)
            parameter = parameter.replace(parameter, casted_parameter)
        parameter += ', '
        print()
        return parameter

    def __call_parameters(self, call: str, func_name: str) -> str:
        from ..functions import get_function_parameters_keys
        model: Llm = self.model
        func_parameters: str = ""
        param_keys = get_function_parameters_keys(
            func_defs=self.func_defs,
            func_name=func_name
        )
        print('Parameters:', end="", flush=True)
        if param_keys:
            self.__set_state(States.PARAMS, param_keys[0])
        else:
            print(' null')
            return "null"
        print()
        prompt: str = self.__get_prompt(call, func_name=func_name)
        prompt += "{"
        prompt += f'"{param_keys[0][0]}":'
        encoded_prompt: list[int] = model.encode_to_int(prompt)
        for k in param_keys:
            key = k[0]
            print(f'\t{key}: ', end="", flush=True)
            prompt_keys = model.encode_to_int(f'"{key}":')
            encoded_prompt.extend(prompt_keys)
            if k[1] == Types.STRING:
                encoded_prompt.extend(model.encode_to_int(' '))
                encoded_prompt.extend(model.encode_to_int('"'))
            self.__set_state(States.PARAMS, k)
            parameter = self.__get_current_parameter(encoded_prompt)
            func_parameters += f'"{key}": {parameter}'
        func_parameters = func_parameters.rstrip(', ')
        print()
        return func_parameters

    def call_functions(
        self, path_output: str = "data/output/function_calls.json"
    ) -> None:
        from ..functions import (
            get_function_defs_struct, get_function_names, store_JSON
        )
        func_defs_struct = get_function_defs_struct(self.func_defs)
        func_names = get_function_names(self.func_defs)
        calls: list[dict[str, Any]] = []
        name: str = ""
        store_JSON(calls, path_output=path_output)
        for call in self.func_calls:
            try:
                name = self.__call_name(
                    call=call.prompt,
                    func_defs=func_defs_struct,
                    func_names=func_names
                )
                if name.rstrip('"').lstrip('"') not in func_names:
                    raise NameError
                parameters = self.__call_parameters(
                    call=call.prompt,
                    func_name=loads(name)
                )
                raw_answer = {
                    "prompt": call.prompt,
                    "name": loads(name),
                    "parameters": loads("{" + parameters + "}")
                }
                calls.append(raw_answer)
                store_JSON(calls, path_output=path_output)
            except JSONDecodeError as e:
                print(
                    f"[ERROR] - {JSONDecodeError.__name__}: "
                    f"the structure of '{name}' "
                    f"is an invalid json. ({e})"
                )
            except NameError:
                print(
                    f"[ERROR] - {NameError.__name__}: "
                    f"the function '{name}' "
                    "doesn't exist in the function definitions."
                )
#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   models.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/15 19:17:30 by varandri            #+#    #+#            #
#   Updated: 2026/10/10 13:27:11 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Data models for function definitions and decoder state.

This module defines the core Pydantic models used to represent function
metadata, input prompts, decoded outputs, and the runtime state of the
decoder.
"""

try:
    from .enums import States, Types
    from pydantic import BaseModel, Field, ConfigDict, model_validator
except (ModuleNotFoundError, ImportError) as e:
    print(f"\n[ERROR] - {e.__class__.__name__}: Missing Module(s).")
    exit()
except (KeyboardInterrupt, EOFError) as e:
    print(
        f"\n[ERROR] - {e.__class__.__name__}: "
        "the program has stopped unexpectedly."
    )
    exit()


class FunctionDefinition(BaseModel):
    """Definition of a callable function.

    Attributes:
        name: Name of the function.
        description: Human-readable description of the function behavior.
        parameters: List of parameter definitions accepted by the function.
        returns: Return schema describing the output value.
    """

    name: str = Field(...)
    description: str = Field(...)
    parameters: dict[str, dict[str, str]] | None = Field(...)
    returns: dict[str, str] = Field(...)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def parameters_validator(self) -> "FunctionDefinition":
        """Validate the function parameters schema."""
        if self.parameters:
            for types in self.parameters.values():
                if len(types.keys()) > 1 or not types.get("type"):
                    raise ValueError(
                        "The format of parameters in functions"
                        " definition is invalid"
                    )
        else:
            self.parameters = None
        return self

    @model_validator(mode="after")
    def returns_validator(self) -> "FunctionDefinition":
        """Validate the function return schema."""
        if not len(self.returns.keys()):
            raise ValueError(
                "The format of returns in functions definition is invalid"
            )
        if not self.returns.get("type") and not self.returns.get("TYPE"):
            raise ValueError(
                "The format of returns in functions definition is invalid"
            )
        return self


class FunctionCalling(BaseModel):
    """A prompt paired with a function call request.

    Attributes:
        prompt: User prompt to be translated into a function call.
    """

    prompt: str = Field(...)
    model_config = ConfigDict(extra="forbid")


class TransitionState(BaseModel):
    """Runtime state tracking for the decoder.

    Attributes:
        state: Active decoding stage, such as name selection or parameter
            extraction.
        type: Current expected parameter type.
    """
    state: States = Field(default=States.NAME)
    parameter_key: tuple[str, Types] | None = Field(default=None)
