# private-gpt

### Installation

This project requires poetry: https://python-poetry.org/docs/

Install the dependencies with.

```bash
poetry install --with ui,local_llm
```

The `ui` and `local_llm` are optional groups if you need that functionality.

### Settings

PrivateGPT can be configured through using yaml files, env variables and profiles.

The full list of properties can be found in [settings.yaml](settings.yaml)

#### env var `PGPT_SETTINGS_FOLDER`

The location of the settings folder. Defaults to the root of the project.

#### env var `PGPT_PROFILES`

Additional profiles to load, format is a comma separated list of profile names.
This will merge `settings-{profile}.yaml` on top of the base settings file.

For example:
`PGPT_PROFILES=local,cuda` will load `settings-local.yaml` and `settings-cuda.yaml`,
their contents will be merged with later profiles properties overriding earlier ones.

During testing, the `test` profile will be active along with the default.

#### Environment variables expansion

Configuration files can contain environment variables, they will be expanded at runtime.

Expansion must follow the pattern `${VARIABLE_NAME:default_value}`.

For example, the following configuration will use the value of the `PORT`
environment variable or `8001` if it's not set.

```yaml
server:
  port: ${PORT:8001}
```

Missing variables with no default will produce an error.

### Running with a local LLM

For LLM to be usable a GPU acceleration is required (CPU execution is possible, but extremely slow), however,
typical Macbook laptops or window desktops lack GPU memory to run even the smallest LLMs.
For that reason **local execution is only supported for models compatible
with [llama.cpp](https://github.com/ggerganov/llama.cpp)**

In particular, these two models (and their variants) work particularly well:

* https://huggingface.co/TheBloke/Llama-2-7B-GGUF
* https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF

Select the quantized version of the model that fits your GPU, download it and place it
under `models/your_quantized_model_of_choice.gguf`

In your `settings-local.yaml` configure the model to use it:

```yaml
llm:
  default_llm: local_llm # Use the local model by default

local_llm:
  enabled: true
  model_name: llama-2-7b-chat.Q4_0.gguf # The name of the model you downloaded
```

### Settings

PrivateGPT can be configured through env variables
using yaml files and profiles.

#### `PGPT_SETTINGS_FOLDER`

The location of the settings folder. Defaults to the root of the project.

#### `PGPT_PROFILES`

Additional profiles to load, format is a comma separated list of profile names.
This will merge `settings-{profile}.yaml` on top of the base settings file.

For example:
`PGPT_PROFILES=local,cuda` will load `settings-local.yaml` and `settings-cuda.yaml`,
their contents will be merged with later profiles properties overriding earlier ones.

During testing, the `test` profile will be active along with the default.

#### Environment variables expansion

Configuration files can contain environment variables, they will be expanded at runtime,

They have to follow the pattern `${VARIABLE_NAME:default_value}`.

For example, the following configuration will use the value of the `PORT`
environment variable or `8001` if it's not set.

```yaml
server:
  port: ${PORT:8001}
```

Missing variables with no default will produce an error.