from enum import Enum
from .point import Point

class PieceType(Enum):
    NONE = -1,
    PAWN = 0,
    KNIGHT = 1,
    BISHOP = 2, 
    ROOK = 3,
    QUEEN = 4,
    KING = 5

class Color(Enum):
    NONE = -1,
    BLACK = 0,
    WHITE = 1

class Piece:
    def __init__(self, piece_type, color):
        self.type = piece_type
        self.color = color

    def __eq__(self, other):
        return self.type == other.type and self.color == other.color

    def __str__(self):
        return self.color.name + ' ' + self.type.name

    def as_notation(self):
        result = ''

        if self.type == PieceType.KNIGHT:
            result = 'N'
        elif self.type == PieceType.NONE:
            result = '0'
        else:
            result = self.type.name[0]

        if self.color == Color.BLACK:
            result = result.lower()

        return result

    #TODO: Add validation for the other pieces
    def is_move_valid(self, source, target):
        if source == target:
            return False
        
        if self.type == PieceType.KING:
            return abs(target.y - source.y) <= 1 and abs(target.x - source.x) <= 1
        elif self.type == PieceType.KNIGHT:
            #not super pretty, but I don't see why not make it the simple way
            if source + Point(1, -2) == target: return True
            if source + Point(2, -1) == target: return True
            if source + Point(2, 1) == target: return True
            if source + Point(1, 2) == target: return True
            if source + Point(-1, 2) == target: return True
            if source + Point(-2, 1) == target: return True
            if source + Point(-2, -1) == target: return True
            if source + Point(-1, -2) == target: return True
            return False
        else:
            return False
        

NullPiece = Piece(PieceType.NONE, Color.NONE)
NullPiece.qhash = 0