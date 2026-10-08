# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: varandri <varandri@student.42antananari    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/09/14 10:11:34 by varandri          #+#    #+#              #
#    Updated: 2026/10/08 21:23:04 by varandri         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

DIR = $(HOME)/goinfre/call_me_maybe

export UV_PROJECT_ENVIRONMENT=$(DIR)/env
export UV_CACHE_DIR=$(DIR)/.cache/uv
export HF_HOME=$(DIR)/.llm

FLAKE8 = $(DIR)/env/bin/flake8
MYPY = $(DIR)/env/bin/mypy

run: install
	@uv run python -m src \
	--functions_definition data/input/functions_definition.json \
	--input data/input/function_calling_tests.json \
	--output data/output/function_calls.json

install:
# 	@pip install uv
	@mkdir -p $(DIR)
	@uv sync

debug: install
	@uv run python -m pdb -m src \
	--functions_definition data/input/functions_definition.json \
	--input data/input/function_calling_tests.json \
	--output data/output/function_calls.json

clean:
	@find . -type d -name "*cache*" | xargs rm -rf
	
lint:
	@$(FLAKE8) . --exclude "llm_sdk/"
	@$(MYPY)  . --exclude "llm_sdk/" --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	@$(FLAKE8) . --exclude "llm_sdk/"
	@$(MYPY)  . --strict --exclude "llm_sdk/"


.PHONY = run install clean lint lint-strict list