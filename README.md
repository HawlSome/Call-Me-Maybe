*This project has been created as part of the 42 curriculum by varandri.*

# call me maybe

Introduction to function calling in LLMs, using constrained decoding on a small language model (Qwen/Qwen3-0.6B).

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

- Python 3.10 or later
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

Generation is split into two stages tracked by a `TransitionState` (`States.NAME`, `States.PARAMS`), so the JSON skeleton is never left to the model. Keys, braces, commas, and quotes are written by the program. The model only fills in values.

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
| `number` / float | tokens of `- . , 0-9` | a comma appears, or the token limit (10) is reached; the value is then cast with `float()` so it is always a valid number (`2` becomes `2.0`) |
| `integer` | same digit mask | a comma or a `.` appears, or the token limit is reached |
| `boolean` | tokens of `true` / `false` | the value is `true` or `false` |
| `string` (and unknown types) | the whole vocabulary | the closing `"` is generated, or the token limit (100) is reached |

For strings, the opening quote is written by the program and the value is closed at the first closing quote the model produces, so the surrounding JSON stays valid.

After each value, the program appends the next key to the prompt (`, "key":`) and moves on. Functions without parameters yield `"parameters": null`.

### Output

Each decoded call is assembled into `{"prompt", "name", "parameters"}`, parsed with `json.loads` to guarantee validity, and appended to the result list. The output file is rewritten after each prompt, so results from earlier prompts survive even if a later one fails.

## Design decisions

- **Pydantic everywhere.** Every class (`FunctionDefinition`, `FunctionCalling`, `TransitionState`, `CallMeMaybe`, `Llm`) inherits from `BaseModel`. Input files are validated on load: `extra="forbid"`, and a validator checks that each parameter has exactly a `type` and that `returns` is well-formed. Malformed definitions fail early with a clear message.
- **Explicit state machine.** The `States` and `Types` enums and the `TransitionState` model keep "what are we generating right now" explicit. The mask builder (`get_options`) only needs that state to decide which tokens are allowed.
- **Separation of concerns.** The decoding loop (`classes/`) is separate from parsing, mapping definitions, mask building, and stop conditions (`functions/`).
- **The program owns the structure.** Keys, delimiters, and brackets are never generated by the model. This is what makes the structure reliable regardless of the model's size.
- **Public SDK API only.** The project uses `encode`, `decode`, `get_logits_from_input_ids`, and `get_path_to_vocab_file`, and no private `llm_sdk` members. No forbidden libraries (transformers, torch, outlines, dspy) are imported.
- **Incremental output.** Results are written after each prompt, and each prompt is processed in its own `try/except`, so one failure does not lose the others.
- **Tooling.** Dependencies are managed with `uv` (`pyproject.toml` + `uv.lock`), and the code follows flake8 and mypy with full type hints and Google-style docstrings.

## Performance analysis

> Fill in with your own measurements before submitting.

- **Accuracy:** [X / N prompts with the correct function and arguments on your test set]. The subject asks for 90%+.
- **Speed:** [total time for N prompts on your machine]. The subject asks for under 5 minutes for all test prompts. Each generated token requires one forward pass, and string generation builds a mask over the full vocabulary, so cost grows with the number and length of generated values.
- **Reliability:** the output is always valid JSON because the skeleton is program-generated, values are parsed before being stored, and numbers are normalized with `float()`. The function name is checked against the definitions before use.

## Challenges faced

- **Tokenization vs. valid strings.** Tokens do not map one-to-one to characters, so masks are built by encoding the expected strings (function names, digits, `true`/`false`) rather than reasoning about characters.
- **Knowing when a value ends.** Numbers, booleans, and strings end differently, and a token can contain both the end of a value and the start of the next delimiter. A per-type stop function (`parameter_ending`) handles this, and the last string token is trimmed at its closing quote.
- **Number formatting.** The model may emit `2` where the schema expects a number. Values are cast to `float` so types always match the definition.
- **Name mask is a token-level approximation.** The name mask allows any token that appears in any function name, not just tokens that continue a valid prefix. The loop stops on an exact match, and a result that is not a known function is rejected rather than emitted. A prefix-based mask (trie) would make selection fully constrained and is a natural improvement.
- **Small-model robustness.** Prompts were worded to give the model a clear role (function selector, parameter retriever) and the exact function structure to refer to.
- **Error handling.** The program handles missing files, invalid JSON, invalid definitions (`ValidationError`), and missing modules with clear messages instead of crashing.

## Testing strategy

> Adapt this section to the tests you actually ran.

- Ran the program on the provided example files and checked that the output file is created, is valid JSON, and has exactly the keys `prompt`, `name`, and `parameters`.
- Verified function names and parameter types against `functions_definition.json`.
- Edge cases: empty strings, large and negative numbers, special characters and quotes in strings, ambiguous prompts, functions with several parameters and with none, and mixed parameter types.
- Error cases: missing input files, invalid JSON, malformed function definitions, unknown parameter types, and an output path in a directory that does not exist.
- Static checks: `make lint` (flake8 + mypy) must pass.

## Resources

### References

- Qwen3 model card: https://huggingface.co/Qwen/Qwen3-0.6B
- Pydantic documentation: https://docs.pydantic.dev/
- NumPy documentation: https://numpy.org/doc/
- Python `json`, `argparse`, and `pathlib` documentation: https://docs.python.org/3/
- uv documentation: https://docs.astral.sh/uv/
- PEP 8 / PEP 257 / flake8 / mypy documentation
- Articles and tutorials on constrained / structured decoding and LLM function calling

### Use of AI

> Replace with an accurate description of how you used AI. The subject requires specifying the tasks and the parts of the project involved.

- [Task, e.g. explaining constrained decoding concepts] — [part of the project]
- [Task, e.g. reviewing code or suggesting test cases] — [part of the project]
- [Task, e.g. drafting this README] — README.md

All AI-generated content was reviewed, tested, and understood before being kept in the project.