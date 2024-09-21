# Track-o-tron

![GitHub Tag](https://img.shields.io/github/v/tag/bendabir/trackotron?sort=semver&label=version)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/trackotron)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/trackotron)
![PyPI - License](https://img.shields.io/pypi/l/trackotron)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/trackotron)
![GitHub deployments](https://img.shields.io/github/deployments/bendabir/trackotron/release?label=release)

Improved decorator for Langfuse. It aims to address some issues of the official Langfuse decorator :

- No tracking of default values
- Messy typing
- Inconsistant behavior between traces and observations
- Poor error handling

> [!WARNING]
> This is still very experimental and definitely not production ready.

## Installation

First, install the package with your favorie package manager (`pip`, `poetry`, etc.).

```python
pip install trackotron
```

## Usage

The observers offer some flexibility. They can be used both as context managers or decorators. When they are used as decorators, the lib is able to observe more data (inputs and outputs, module name, function name, etc.).

In both cases, it offers an access to the observation client through a proxy. This is useful to inject a score, or any other custom thing. The proxy can store updates until the function is terminated (or the context manager exits) to avoid useless API calls.

First, an observer needs to be instantiated. It will create required contexts.

```python
from langfuse import Langfuse
from trackotron import Observer

client = Langfuse()
observer = Observer(client)
```

Then, any function can be decorated. The proxy will be automatically injected. By default, it will capture both the input and the output, but this can be tuned with `capture_input=False` or `capture_output=False`.

```python
from trackotron import GenerationProxyAlias, GenerationUpdate

@observer.observe(type_="generation")
def run(proxy: GenerationProxyAlias, model: str = "gpt-4o-mini") -> str:
  # ...
  proxy.update(GenerationUpdate(model=model))
```

It can also be used as a context manager. Some parameters (such as `capture_input` or `capture_output`) won't have any effect in such situation.

```python
with observer.observe(name="context") as proxy:
  # ...
  proxy.score("perplexity", 1.0, comment="Lorem ipsum")
```

### Limitations

The decorator currently only supports functions. Instance and class methods are not supported regarding typing (but it should work).

Coroutines are not supported yet but it should be pretty straight forward to implement. The only issue is to find a way to avoid code duplication.

## Performances

The overhead appears to be quite small. The scripts ([`benchmark`](./scripts/benchmark.py) and [`baseline`](./scripts/baseline.py)) are used to quickly measure performances of Langfuse (both when enabled or disabled) compared to a raw script. It contains some sleeps (1.50s) to fake some execution or I/O.

| Baseline | Langfuse Disabled | Langfuse Enabled        |
| -------- | ----------------- | ----------------------- |
| 1.5017   | 1.5062 (+0.30%)   | 1.5080 (+0.42%, +0.12%) |

The overhead is between 0.30% and 0.42% (depending if Langfuse is enabled). This should be pretty okay for most of the LLM applications which often only do HTTP calls.

## Development

The whole project relies on Poetry for setup. It has been developed with Python 3.9 for backward compatibility. Python 3.8 is not supported as it will reach end-of-life in October 2024.

### Environment

```bash
poetry env use python3.9
poetry lock
poetry install --with dev
poetry run pre-commit install
```

### Quality

```bash
poetry run black . # Format code
poetry run ruff check --fix --force-exclude . # Lint code
poetry run mypy --ignore-missing-imports --scripts-are-modules . # Type check code
```

```bash
poetry run python -m pytest --cov=src/trackotron tests # Run all tests
```

### Build

```bash
poetry build -f wheel
```

### TODOs

Here are some ideas to improve the current decorator :

- [ ] Support coroutines
- [ ] Fix typing for instance and class methods
- [ ] Make the proxy injection optional (_i.e._ do not inject the proxy if not present in the function/method signature)
- [ ] Add more tests to ensure behaviors and consistency
- [ ] Support context reuse if that makes sense
- [ ] Handle data obfuscation when needed so we don't expose secrets.
- [ ] Make parenthesis usage optional (see [#918](https://github.com/langfuse/langfuse-python/pull/918))
