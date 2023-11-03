# Creating the development environment

1. Install [Pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)
2. Install [PipX](https://github.com/pypa/pipx?tab=readme-ov-file#install-pipx)
3. Install [Poetry](https://python-poetry.org/docs/#installing-with-pipx) with **PipX**
4. install [Tox](https://tox.wiki/en/latest/installation.html#via-pipx) with **PipX**
5. Install necessary python versions

    `pyenv install --skip-existing 3.8 3.9 3.10 3.11 3.12`

6. Set python versions as local

    `pyenv local 3.12 3.11 3.10 3.9 3.8`

7. Ensure poetry config

    `poetry config virtualenvs.create true`

    `poetry config virtualenvs.prefer-active-python true`
8. Install the lib and dependencies with poetry

    `poetry install --all-extras`

9. Initialize pre-commit

    `poetry run pre-commit install`



# Running tests
To run the tests you can use any of the commands bellow:

1. `make tests` To run all tests over all environment combinations
2. `make test-latest` To run all tests over the latest enviroment possible

# Running code quality tools
To options to run the linters are:

1. `make isort`
2. `make black`
3. `make pylint`
4. `make bandit`
5. `make mypy`

To run all linters over all files: `make lint`
