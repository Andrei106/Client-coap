import logging
import uuid


class TokenGenerator:
    state = {}

    def __init__(self):
        logging.info('Initialized token generator')
        self.state['algorithm'] = 'TBD'

    def __new__(cls, *args, **kwargs):
        if not(hasattr(cls, 'instance')):
            cls.instance = super(TokenGenerator, cls).__new__(cls, *args, **kwargs)
            cls.instance.__dict__ = cls.state
        return cls.instance

    def get_token(self):
        logging.info(f'Generating token with alg {self.state["algorithm"]}')
        #TODO: actually generate tokens and use them
        return f'{uuid.uuid4().int}'[:8]

    def get_message_id(self):
        logging.info(f'Generating message ID  with alg {self.state["algorithm"]}')
        # TODO: actually generate tokens and use them
        return f'{uuid.uuid4().int >> 112}'
