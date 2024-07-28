from abc import ABC, abstractmethod

class BaseAPI(ABC):

    @abstractmethod
    def __init__(self):
        self.base_url = None
        self.headers = None

    @abstractmethod
    def store_token(self, token):
        pass

    @abstractmethod
    def get_stored_token(self):
        pass

    @abstractmethod
    def get_cgm_data(self):
        pass

    @abstractmethod
    def formatData(self, graph_data):
        pass

    @abstractmethod
    def get_last_cgm_value(self, values):
        pass
    
    @abstractmethod
    def login(self):
        pass