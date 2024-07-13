# Bot

![run main.py](https://github.com/r-engres/bot/actions/workflows/run.yml/badge.svg)

## Guide

1. Install Poetry.
2. Install the dependencies
    ```bash
    poetry install
    ```
3. Activate the virtual environment
    ```bash
    poetry shell
    ```
4. Run the bot
    ```bash
    python src/main.py
    ```


To add a new dependency, run:
```bash
poetry add PACKAGE
```

To add a new development dependency, run:
```bash
poetry add --group dev PACKAGE
```

To format the code, run:
```bash
black src
```

To sort the imports, run:
```bash
isort src
```

To lint the code, run:
```bash
ruff check src
```

To statically type-check the code, run:
```bash
pyright src
```