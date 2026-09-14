# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: varandri <varandri@student.42antananari    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/09/14 10:11:34 by varandri          #+#    #+#              #
#    Updated: 2026/09/14 12:12:06 by varandri         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

DIR = $(HOME)/goinfre/call_me_maybe

export UV_PROJECT_ENVIRONMENT=$(DIR)/env
export UV_CACHE_DIR=$(DIR)/.cache/uv

FLAKE8 = $(DIR)/env/bin/flake8

run: install
	@uv run -m src

install:
	@mkdir -p $(DIR)
	@uv sync

list: install
	uv pip list --python $(DIR)/env/bin/python
	
lint:
	@$(FLAKE8) .	

.PHONY = install run clean fclean list