#!/bin/bash

current_python_version_number=$(python3 --version | cut -d' ' -f2 )

this_config="""
# See https://pre-commit.com for more information
# See https://pre-commit.com/hooks.html for more hooks
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
    -   id: check-ast
    -   id: check-case-conflict
    -   id: check-docstring-first
    -   id: check-json
    -   id: check-merge-conflict
    -   id: detect-aws-credentials
        args: [--allow-missing-credentials]
    -   id: detect-private-key
    -   id: name-tests-test
    -   id: pretty-format-json
    -   id: requirements-txt-fixer
-   repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.10.0.1
    hooks:
    -   id: shellcheck
# Using this mirror lets us use mypyc-compiled black, which is about 2x faster
-   repo: https://github.com/psf/black-pre-commit-mirror
    rev: 25.1.0
    hooks:
    - id: black
    # It is recommended to specify the latest version of Python
    # supported by your project here, or alternatively use
    # pre-commit's default_language_version, see
    # https://pre-commit.com/#top_level-default_language_version
    language_version: python$current_python_version_number
"""


# Check if pre-commit is installed
pip3 show "pre-commit" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Installing pre-commit..."
    pip3 install pre-commit
else
    echo "pre-commit is already installed"
fi


echo "$this_config" > ./.pre-commit-config.yaml


# Ask user if they want to install pre-commit hooks
read -p "Would you like to install pre-commit hooks? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pre-commit install
else
    echo "Skipping pre-commit hooks installation"
fi

pre-commit run --all-files
