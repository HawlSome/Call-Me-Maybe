#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   call_me_maybe.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/05 11:20:32 by varandri            #+#    #+#            #
#   Updated: 2026/10/08 01:19:17 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    from typing import Any
    from .enums import States, Types
    from pydantic import BaseModel, Field, ConfigDict
    from .models import FunctionCalling, FunctionDefinition, TransitionState
    from .llm_wrapper import Llm
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
    model: Llm = Field(default=Llm())
    func_defs: list[FunctionDefinition] = Field(default=...)
    func_calls: list[FunctionCalling] = Field(default=...)
    transition_state: TransitionState = Field(default=TransitionState())
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __set_state(
        self, state: States = States.NAME,
        param_keys: tuple[str, Types] | None = None
    ) -> None:
        transition_state: TransitionState = self.transition_state
        transition_state.state = state
        transition_state.parameter_key = param_keys

    def __call_name(self, call: str, func_defs: list[dict[str, Any]]) -> str:
        from ..functions import get_options
        self.__set_state()
        print(f'Prompt: "{call}".')
        print("Function Name: ", end="", flush=True)
        model: Llm = self.model
        func_name = ""
        max_token = 20
        name_options = get_options(caller=self)
        prompt = (
            "You are a function selector.\n"
            "You will select a function_name from "
            "a list of given function definitions.\n"
            "You will chose the function that match the one "
            "described in a given prompt.\n"
            'the format is as: "name": "fn_function_name".\n'
            f"Function Definitions: {func_defs}. Output:"
            '{'f'"prompt":"{call}", "name":'
        )
        encoded_prompt = model.encode_to_int(prompt)
        while True:
            best_token = model.get_best_token(
                prompt=encoded_prompt, options=name_options
            )
            decoded_token = model.decode([best_token])
            max_token -= 1
            supposition: str = func_name + decoded_token
            if (
                max_token <= 0 or
                (
                    supposition.startswith('"') and
                    supposition.endswith('"')
                )
            ):
                break
            print(f"{decoded_token}", end="", flush=True)
            func_name += decoded_token
            encoded_prompt.append(best_token)
        self.__set_state(States.PARAMS)
        print("\n")
        return func_name

    def call_functions(self) -> None:
        from ..functions import get_function_defs_struct
        func_defs_struct = get_function_defs_struct(self.func_defs)
        self.__call_name(
            call=self.func_calls[0].prompt,
            func_defs=func_defs_struct
        )
