from enum import IntEnum
from .point import Point

import copy

class PieceType(IntEnum):
    NONE = -1,
    PAWN = 0,
    KNIGHT = 1,
    BISHOP = 2, 
    ROOK = 3,
    QUEEN = 4,
    KING = 5

class Color(IntEnum):
    NONE = -1,
    BLACK = 0,
    WHITE = 1

    def opposite(color):
        if color == Color.NONE:
            return Color.NONE
        else:
            return Color.WHITE if color == Color.BLACK else Color.BLACK

class Piece:
    def __init__(self, piece_type, color):
        self.type = piece_type
        self.color = color
        self.collapsed = True

    def __eq__(self, other):
        return self.type == other.type and self.color == other.color

    def __str__(self):
        return self.color.name + ' ' + self.type.name

    def copy(self):
        #no need to copy NullPiece
        if self == NullPiece:
            return NullPiece

        #just in case new variables are added in other places
        return copy.copy(self)

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

    #create a new instance of class from notation ('P', 'K', 'q', etc)
    def from_notation(notation):
        piece = Piece(PieceType.NONE, Color.NONE)

        if notation == '0':
            piece = NullPiece
        else:
            if notation.islower():
                piece.color = Color.BLACK
                notation = notation.upper()
            else:
                piece.color = Color.WHITE

            if notation == 'N':
                piece.type = PieceType.KNIGHT
            elif notation == 'P':
                import qchess.pawn 

                return qchess.pawn.Pawn(piece.color)
            else:
                remaining_types = [PieceType.KING, PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP]

                for ptype in remaining_types:
                    if ptype.name[0] == notation:
                        piece.type = ptype
                        break

        return piece
        

    def is_move_slide(self):
        return (
            self.type == PieceType.BISHOP or
            self.type == PieceType.ROOK or
            self.type == PieceType.QUEEN
        )

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
        elif self.type == PieceType.ROOK:
            return source.x == target.x or source.y == target.y
        elif self.type == PieceType.BISHOP:
            vec = target - source
            return abs(vec.x) == abs(vec.y)
        elif self.type == PieceType.QUEEN:
            return (
                Piece(PieceType.ROOK, self.color).is_move_valid(source, target) or
                Piece(PieceType.BISHOP, self.color).is_move_valid(source, target)
            )
        else:
            return False
        

NullPiece = Piece(PieceType.NONE, Color.NONE)
NullPiece.collapsed = True