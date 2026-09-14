# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: varandri <varandri@student.42antananari    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/09/14 10:11:34 by varandri          #+#    #+#              #
#    Updated: 2026/09/14 12:39:13 by varandri         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

DIR = $(HOME)/goinfre/call_me_maybe

export UV_PROJECT_ENVIRONMENT=$(DIR)/env
export UV_CACHE_DIR=$(DIR)/.cache/uv

FLAKE8 = $(DIR)/env/bin/flake8
MYPY = $(DIR)/env/bin/mypy

run: install
	@uv run -m src

install:
	@mkdir -p $(DIR)
	@uv sync
	
lint:
	@$(FLAKE8) . --exclude "llm_sdk/"
	@$(MYPY)  . --exclude "llm_sdk/" --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	@$(FLAKE8) . --exclude "llm_sdk/"
	@$(MYPY)  . --strict --exclude "llm_sdk/"

clean:
	@find . -type d -name "*cache*" | xargs rm -rf

list: install
	uv pip list --python $(DIR)/env/bin/python

.PHONY = run install clean lint lint-strict list