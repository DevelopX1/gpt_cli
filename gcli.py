#!/usr/bin/env python3.7
from optparse import OptionParser
from pathlib import Path
import configparser
import openai
import locale
import sys
import os

CONFIG_NAME = '.gpt.conf'
OPENAI_TEXT_MODEL = 'text-davinci-003'
OPENAI_MAX_TOKENS = 1000
CONFIG_DEFAULT_SECTION = 'default'
CONFIG_DEFAULT_PATH = os.path.join(Path.home(), CONFIG_NAME)


parser = OptionParser()
parser.add_option('--configure',
                    action="store_true",
                    help='Start configure')

(options, args) = parser.parse_args()

"""
Exception list
"""
class NoDefaultConfigSection(Exception):
    def __init__(self, config_file_path):
        """
        Called if there is no default section in the configuration file
        """
        self.message = f'Missing [default] section in config file - {config_file_path}'
        super().__init__(self.message)


class PromptIsEmpty(Exception):
    def __init__(self):
        """
        Called if you didn't ask a question
        """
        self.message = f'You didn\'t ask a question, please, see help'
        super().__init__(self.message)

class EmptyResponse(Exception):
    def __init__(self):
        """
        Called if no response is received from OpenAI
        """
        self.message = f'Unknown error'
        super().__init__(self.message)

"""
function to save OpenAItoken to config file
"""
def configure(config_file_path):
    openai_token = input('Please, enter OpenAi token: ')
    if openai_token:
        config_file = open(config_file_path, 'w')
        config_file.write(f'[default]\nOPENAI_API_TOKEN={openai_token}')
        config_file.close()

"""
Request for OpenAI, 
get prompt, return text
"""
def openai_request(text: str) -> str:
    response = openai.Completion.create(
            model=OPENAI_TEXT_MODEL,
            prompt=text,
            max_tokens=OPENAI_MAX_TOKENS
    )

    if 'text' in response.choices[0]:
        return response.choices[0]['text']
    else:
        raise EmptyResponse

"""
Here is the main logic
"""
if __name__ == '__main__':
    if options.configure:
        configure(CONFIG_DEFAULT_PATH)
        exit(0)

    if not os.path.isfile(CONFIG_DEFAULT_PATH):
        configure(CONFIG_DEFAULT_PATH)
    else:
        config = configparser.ConfigParser()
        config.read(CONFIG_DEFAULT_PATH)

        if CONFIG_DEFAULT_SECTION not in config.sections():
            raise NoDefaultConfigSection

        if not args:
            raise PromptIsEmpty

        openai.api_key = config[CONFIG_DEFAULT_SECTION]['OPENAI_API_TOKEN']
        print(openai_request(args[0]))


