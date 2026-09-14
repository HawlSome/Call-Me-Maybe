# ########################################################################### #
#                                                                             #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: varandri <varandri@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/14 10:11:43 by varandri            #+#    #+#            #
#   Updated: 2026/09/14 13:49:30 by varandri           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

try:
    import argparse
    from llm_sdk import Small_LLM_Model
except ModuleNotFoundError as e:
    print(f"[ERROR]: {e}")
    exit()


def main() -> None:
    argparse
    sm = Small_LLM_Model()
    print("Hello from cmm!")


if __name__ == "__main__":
    main()
