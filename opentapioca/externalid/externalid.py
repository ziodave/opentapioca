from abc import ABC, abstractmethod


class ExternalId(ABC):

    @abstractmethod
    def get(self, item):
        pass
