*This project has been created as part of the 42 curriculum by varandri.*

# call me maybe
## Description

Large language models understand natural language but do not reliably produce structured, machine-executable output. A 0.6B-parameter model asked to emit JSON will often fail.

**call me maybe** translates a natural-language prompt into a structured function call. Given `"What is the sum of 40 and 2?"`, the program does not answer `42`. It returns the function to call and its typed arguments:

```json
{
    "prompt": "What is the sum of 40 and 2?",
    "name": "fn_add_numbers",
    "parameters": {"a": 40.0, "b": 2.0}
}
```

The program reads:

- a list of function definitions (name, description, parameters with types, return type),
- a list of natural-language prompts.

It writes a JSON file containing, for each prompt, the original `prompt`, the selected function `name`, and its `parameters`.

The function is chosen by the LLM itself, and the structure of the output is enforced token by token through constrained decoding rather than by prompting alone.

### Project structure

```
.
├── llm_sdk/                  # provided wrapper around Qwen3-0.6B
├── data/input/               # functions_definition.json, function_calling_tests.json
├── src/
│   ├── __main__.py           # CLI entry point and top-level error handling
│   ├── classes/
│   │   ├── call_me_maybe.py  # decoding pipeline (name + parameters)
│   │   ├── llm_wrapper.py    # typed wrapper: encode, decode, masked argmax
│   │   ├── models.py         # pydantic models (definitions, prompts, state)
│   │   └── enums.py          # States and Types enums
│   └── functions/
│       ├── parser.py         # argparse, JSON loading, JSON output
│       ├── model_mappers.py  # definitions -> names, structures, parameter types
│       ├── mask_helpers.py   # allowed-token masks per decoding state
│       └── helpers.py        # stop conditions for parameter values
├── pyproject.toml
├── uv.lock
├── Makefile
└── README.md
```

## Instructions

### Requirements

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/)
- Dependencies (installed by `uv sync`): `numpy`, `pydantic`
- The `llm_sdk` package, copied at the repository root next to `src/`

### Installation

```bash
make install        # runs uv sync
```

### Running

```bash
uv run python -m src [--functions_definition <file>] [--input <file>] [--output <file>]
```
or 
```bash
make 
```
Defaults:

| Argument | Default |
|---|---|
| `--functions_definition` | `data/input/functions_definition.json` |
| `--input` | `data/input/function_calling_tests.json` |
| `--output` | `data/output/function_calling_results.json` |

The output directory is created automatically if it does not exist.

### Makefile rules

| Rule | Description |
|---|---|
| `install` | Install dependencies with uv |
| `run` | Run the main program |
| `debug` | Run the program under `pdb` |
| `clean` | Remove `__pycache__`, `.mypy_cache`, and other temporary files |
| `lint` | `flake8 .` and `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs` |
| `lint-strict` | `flake8 .` and `mypy . --strict` |

## Example usage

```bash
# Default paths
uv run python -m src

# Custom paths
uv run python -m src \
    --functions_definition data/input/functions_definition.json \
    --input data/input/function_calling_tests.json \
    --output data/output/function_calling_results.json
```

Example `functions_definition.json` entry:

```json
{
    "name": "fn_greet",
    "description": "Generate a greeting message for a person by name.",
    "parameters": {"name": {"type": "string"}},
    "returns": {"type": "string"}
}
```

Example `function_calling_tests.json`:

```json
[
    {"prompt": "What is the sum of 2 and 3?"},
    {"prompt": "Greet shrek"},
    {"prompt": "Reverse the string 'hello'"}
]
```

Example output:

```json
[
    {
        "prompt": "What is the sum of 2 and 3?",
        "name": "fn_add_numbers",
        "parameters": {"a": 2.0, "b": 3.0}
    },
    {
        "prompt": "Reverse the string 'hello'",
        "name": "fn_reverse_string",
        "parameters": {"s": "hello"}
    }
]
```

While running, the program streams the generation to the terminal (prompt, selected function name, then each parameter as it is decoded).

## Algorithm explanation

### Principle

At each step the model produces logits over its whole vocabulary. Instead of taking the argmax over all tokens, the program builds the set of **allowed token IDs** for the current state, sets every other logit to `-inf`, and takes the argmax of what remains (`Llm.get_best_token`). The chosen token is appended to the prompt and the loop repeats. The model can only ever emit tokens that fit the structure we are currently building.

Generation is split into two stages tracked by a `TransitionState` (`States.NAME`, `States.PARAMS`).

### Stage 1: function selection (`States.NAME`)

1. The prompt lists the serialized function definitions and ends with `{"prompt": "<user prompt>", "name": `.
2. The allowed tokens are the union of the token IDs obtained by encoding each function name from the definitions.
3. Tokens are chosen greedily under that mask, one by one, and decoded and concatenated.
4. Generation stops as soon as the accumulated string equals one of the valid function names, or after 20 tokens.
5. If the result is not a valid name, the prompt is reported as an error (`NameError`) and skipped, so a bad selection never produces a malformed entry.

### Stage 2: parameter extraction (`States.PARAMS`)

The parameters are read from the definition of the selected function, in order. The program writes the JSON skeleton (`{"key":`) into the prompt and lets the model generate each value under a type-specific mask:

| Type (from definition) | Allowed tokens | Stop condition |
|---|---|---|
| `number` / float | tokens of `- . , 0-9` | a comma appears, or the token limit (30) is reached; the value is then cast with `float()` so it is always a valid number (`2` becomes `2.0`) |
| `integer` | same digit mask | a comma or a `.` appears, or the token limit is reached |
| `boolean` | tokens of `true` / `false` | the value is `true` or `false` |
| `string` (and unknown types) | the whole vocabulary except anything containing '\\"' | the closing `"` is generated, or the token limit (100) is reached |

For strings, the opening quote is written by the program and the value is closed at the first closing quote the model produces, so the surrounding JSON stays valid.

After each value, the program appends the next key to the prompt (`, "key":`) and moves on. Functions without parameters yield `"parameters": {}`.

### Output

Each decoded call is assembled into `{"prompt", "name", "parameters"}`, parsed with `json.loads` to guarantee validity, and appended to the result list. The output file is rewritten after each prompt, so results from earlier prompts survive even if a later one fails.

## Design decisions

- **Explicit state machine.** The `States` and `Types` enums and the `TransitionState` model keep "what are we generating right now" explicit. The mask builder (`get_options`) only needs that state to decide which tokens are allowed.
- **Jump-forward-decoding**: Skipping unchanged and predictable value inside the Json, this keeps the structure unchanged and the correctness high. 
- **Separation of concerns.** The decoding loop (`classes/`) is separate from parsing, mapping definitions, mask building, and stop conditions (`functions/`).
- **The program owns the structure.** Keys, delimiters, and brackets are never generated by the model. This is what makes the structure reliable regardless of the model's size.
- **Incremental output.** Results are written after each prompt, and each prompt is processed in its own `try/except`, so one failure does not lose the others.


## Performance analysis


- **Accuracy:**  11/ 11 prompts with the correct function and arguments on the actual test set.
- **Speed:** 1~2 minutes for the actual test set.
- **Reliability:** the output is always valid JSON because the skeleton is program-generated, values are parsed before being stored.. The function name is checked against the definitions before use. in some case of malformed string type value , the function call containing it is skipped (very rare case).

## Challenges faced
|Challenge|Solution
|---------|--------
**Knowing the values to mask.** Name, Parameters, numeric parameters and boolean parameters are masked differently|A State to track specific value maks for each one of the State types.
**Knowing when a value ends.** Numbers, booleans, and strings end differently|A per-type stop function (`parameter_ending`) handles this, and the last string token is trimmed at its closing quote.
**Number formatting.** The model may emit an int where the schema expects a float| Values are cast to `float` when needed.
**Generation Time** The program took over 5 minutes to generate the whole Json. | Jump-forward-decoding was used to skip the generation for predictable charater/words, making the model generate only at part where multiple candidate exists for choice .

## Testing strategy

- Ran the program on the provided example files and checked that the output file is created, is valid JSON, and has exactly the keys `prompt`, `name`, and `parameters`.
- Verified function names and parameter types against `functions_definition.json`.
- Edge cases: empty strings, large and negative numbers, special characters and quotes in strings, ambiguous prompts, functions with several parameters and with none, and mixed parameter types added on the input files then running the program.
- Static checks: `make lint` to test the norm of the codes.

## Resources

### References

- [Constrained Decoding](https://www.aidancooper.co.uk/constrained-decoding/): Explanation of constrained decoding
- [Jump-Forward-Decoding](https://www.lmsys.org/blog/2024-02-05-compressed-fsm/): Explanation of Jump-Forward-Decoding
- [Function Calling](https://developers.openai.com/api/docs/guides/function-calling?api-mode=responses): Explanation of function Calling
- [Youtube](https://www.youtube.com/watch?v=7xTGNNLPyMI&t=1229s): Video explaining how AI works internally
- [Pydantic](https://docs.pydantic.dev/): Documentation of Pydantic
- [Numpy](https://numpy.org/doc/stable/): Documentation of Numpy
- [Python](https://docs.python.org/3/): Usage of `json`, `argparse`, and `pathlib`

### Use of AI

- suggesting test cases — the whole project
- improving the structure of the README — README.md
