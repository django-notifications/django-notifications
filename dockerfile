#!/bin/sh
FROM python:3.11-slim-buster

SHELL ["/bin/bash", "-c"]

RUN apt-get update
RUN apt-get install -y curl git gcc make zlib1g-dev libssl-dev libffi-dev sqlite3 libsqlite3-dev liblzma-dev
RUN pip install --upgrade pip

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN curl https://pyenv.run | bash

ENV PATH ~/.pyenv/shims:~/.pyenv/bin:/root/.local/bin:$PATH
RUN eval "$(pyenv init -)"
RUN pyenv install 3.8 3.9 3.10

WORKDIR /django-notifications
RUN pyenv local system 3.8 3.9 3.10

RUN apt-get --purge autoremove -y gnupg; \
    rm -rf /var/cache/apt/lists;

ENTRYPOINT poetry install && poetry run -- pre-commit install && /bin/bash
