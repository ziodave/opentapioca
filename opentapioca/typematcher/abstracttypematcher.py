from abc import ABC, abstractmethod


class AbstractTypeMatcher(ABC):

    def __init__(self, subclass_pid='P279'):
        self.subclass_pid = subclass_pid
        super().__init__()

    @abstractmethod
    def is_subclass(self, qid_1, qid_2):
        pass
