#!/usr/bin/env python3.7
from optparse import OptionParser
from termcolor import colored
from pathlib import Path
from sys import exit
import configparser
import orm_sqlite  
import openai
import os

OPENAI_MAX_TOKENS = 1000
CONFIG_NAME = '.gpt.conf'
OPENAI_TEXT_MODEL = 'text-davinci-003'
HITSORY_FILE_NAME = '.gpt_cli_history.db'
CONFIG_DEFAULT_SECTION = 'default'
CONFIG_DEFAULT_PATH = os.path.join(Path.home(), CONFIG_NAME)
HISTORY_FILE_ABS_PATH = os.path.join(Path.home(), HITSORY_FILE_NAME)
COLORS = {
    'hisotory_responce_color': 'white',
    'hisotory_request_color': 'green',
    'term_responce_color': 'white'
}

parser = OptionParser()
parser.add_option('--configure',
                    action="store_true",
                    help='Start configure')
parser.add_option('--history',
                    action="store_true",
                    help='Show history of requests and responces')

(options, args) = parser.parse_args()

"""
Exception list
"""
class NoDefaultConfigSection(Exception):
    def __init__(self, config_file_path: str):
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

class EmptyToken(Exception):
    def __init__(self):
        """
        Called if the token is not specified
        """
        self.message = f'Token is not specified'
        super().__init__(self.message)


"""
all query history is stored in sqlite database by
reference in HISTORY_FILE_ABS_PATH variable
"""
class History(orm_sqlite.Model):  
    id = orm_sqlite.IntegerField(primary_key=True) 
    request = orm_sqlite.StringField()
    responce = orm_sqlite.StringField()


"""
Add history
"""
def write_history(question, answer):
    return History({'request': question, 'responce': answer}).save()


"""
Show history
"""
def show_history(history_file_path):
    for obj in History.objects.all():
        print(colored(obj['request'], COLORS['hisotory_request_color'],
                                      attrs=['bold']), end='⬇️')
        print(colored(obj['responce'], COLORS['hisotory_responce_color']))


"""
function to save OpenAItoken to config file
"""
def configure(config_file_path: str):
    openai_token = input('Please, enter OpenAi token: ')
    if openai_token:
        with open(config_file_path, 'w') as file:
            file.write(f'[default]\nOPENAI_API_TOKEN={openai_token}')
    else:
        raise EmptyToken

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
    db = orm_sqlite.Database(HISTORY_FILE_ABS_PATH)
    History.objects.backend = db

    if options.configure:
        configure(CONFIG_DEFAULT_PATH)
        exit(0)

    if options.history:
        show_history(HISTORY_FILE_ABS_PATH)
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
        answer = openai_request(args[0])
        write_history(args[0], answer)
        print(colored(answer, COLORS['term_responce_color'], attrs=['bold']))
