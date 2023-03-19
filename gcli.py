#!/usr/bin/env python3.7

from exceptions import NoDefaultConfigSection, PromptIsEmpty, EmptyResponse, EmptyToken
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from difflib import SequenceMatcher
from optparse import OptionParser
from termcolor import colored
from pathlib import Path
from sys import exit
import configparser 
import openai
import os

OPENAI_MAX_TOKENS = 1000
HISTORY_MACH_PROC = 0.70
CONFIG_NAME = '.gpt.conf'
OPENAI_TEXT_MODEL = 'text-davinci-003'
HITSORY_FILE_NAME = '.gpt_cli_history.db'
CONFIG_DEFAULT_SECTION = 'default'
CONFIG_DEFAULT_PATH = os.path.join(Path.home(), CONFIG_NAME)
HISTORY_FILE_ABS_PATH = os.path.join(Path.home(), HITSORY_FILE_NAME)
COLORS = {
    'hisotory_responce_color': 'white',
    'hisotory_request_color': 'green',
    'term_responce_color': 'white',
    'resp_from_history': 'yellow'
}


# Connector
engine = create_engine(f'sqlite:///{HISTORY_FILE_ABS_PATH}', echo=False)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()
Base = declarative_base()

parser = OptionParser()
parser.add_option('--configure',
                    action="store_true",
                    help='Start configure')
parser.add_option('--history',
                    action="store_true",
                    help='Show history of requests and responces')
parser.add_option('--forse_search',
                    action="store_true",
                    help='Show history of requests and responces')

(options, args) = parser.parse_args()


"""
all query history is stored in sqlite database by
reference in HISTORY_FILE_ABS_PATH variable
"""
class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key = True)
    request = Column(String, unique = False)
    responce = Column(String, unique = False)

    def __init__(self, request, responce):
        self.request = request
        self.responce = responce
        

"""
If there is a similar request in the history, then return it
"""
def history_matcher(text: str) -> str:
    data = {}

    for obj in session.query(History).filter(History.request.like(f'%{text}%')).all():
        request = obj.request
        request_check = SequenceMatcher(None, request, text).ratio()
        
        if request_check >= HISTORY_MACH_PROC:
            data[request_check] = request
    
    if len(data) >= 1:
        return data[max(data.keys())]

    return None

"""
Here we are looking for answers that were
previously on a duplicate request
"""
def find_history(text: str):
    history_obj = session.query(History).filter(History.request == text).all()

    print(colored('From history (to use ChatGPT add --forse_search option)',
                        COLORS['resp_from_history'],
                        attrs=['bold']))

    for history in history_obj:
        print(colored(f'{history.id}. {history.responce}', COLORS['term_responce_color']))

"""
Add history
"""
def write_history(question: str, answer: str):
    session.add(History(question, answer))

"""
Show history
"""
def show_history(history_file_path: str):
    for obj in session.query(History).all():
        print(colored(obj.request, COLORS['hisotory_request_color'],
                                      attrs=['bold']), end='⬇️\n')
        print(colored(obj.responce, COLORS['hisotory_responce_color']))


"""
function to save OpenAItoken to config file
"""
def configure(config_file_path: str):
    Base.metadata.create_all(engine)
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
        matcher_history = history_matcher(args[0])

        if matcher_history and not options.forse_search:
            find_history(matcher_history)
        # else:
        #     answer = openai_request(args[0])
        #     write_history(args[0], answer)
        #     print(colored(answer, COLORS['term_responce_color']))
        #     session.flush()
        #     session.commit()
