from abc import ABC, abstractmethod

class BaseEngine(ABC):
    """
        Any engine must implement these methods,
        as they are required by the QChess class.
    """

    @abstractmethod
    def get_all_entangled_points(self, x, y):
        raise NotImplementedError()

    @abstractmethod
    def collapse_point(self, x, y):
        raise NotImplementedError()

    @abstractmethod
    def collapse_all(self):
        raise NotImplementedError()

    @abstractmethod
    def on_add_piece(self, x, y, piece):
        raise NotImplementedError()

    @abstractmethod
    def standard_move(self, source, target, force=False):
        raise NotImplementedError()

    @abstractmethod
    def split_move(self, source, target1, target2):
        raise NotImplementedError()

    @abstractmethod
    def merge_move(self, source1, source2, target):
        raise NotImplementedError()
