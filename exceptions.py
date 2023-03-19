"""
Exception list
"""
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
