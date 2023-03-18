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
