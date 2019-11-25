from abc import ABC, abstractmethod

"""
Methods any engine must implement.
"""
class BaseEngine(ABC):
    """
    Get all the points entangled with point (x, y)

    Required by QChess to display entangled points of the different pieces.
    """
    @abstractmethod
    def get_all_entangled_points(self, x, y):
        raise NotImplementedError()


    """
    Callback for when a new piece is created.
    Engine can use it to change internal simulation info regarding that new piece.

    Required by QChess.
    """
    @abstractmethod
    def on_add_piece(self, x, y, piece):
        raise NotImplementedError()

    """
    Implements the standard move operation internally.

    Required by QChess.
    """
    @abstractmethod
    def standard_move(self, source, target, force=False):
        raise NotImplementedError()

    
    """
    Implements the split move operation internally.

    Required by QChess.
    """
    @abstractmethod
    def split_move(self, source, target1, target2):
        raise NotImplementedError()


    """
    Implements the merge move operation internally.

    Required by QChess.
    """
    @abstractmethod
    def merge_move(self, source1, source2, target):
        raise NotImplementedError()

    """
    Collapse all pieces entangled with a the piece on (x, y)

    Required to perform tests.
    """
    @abstractmethod
    def collapse_point(self, x, y):
        raise NotImplementedError()


    """
    Collapse all points in the board.

    Required to perform tests.
    """
    @abstractmethod
    def collapse_all(self):
        raise NotImplementedError()
