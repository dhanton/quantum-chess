from .piece import *

class Pawn(Piece):
    class MoveType(IntEnum):
        INVALID = 0,
        SINGLE_STEP = 1,
        DOUBLE_STEP = 2,
        CAPTURE = 3,
        EN_PASSANT = 4


    def __init__(self, color):
        super().__init__(PieceType.PAWN, color)
        
        self.has_moved = False

    #we need to access the quantum chess to check type of piece
    #since capture and move have diferent validations
    def is_move_valid(self, source, target, qchess=None):
        if source == target:
            return Pawn.MoveType.INVALID, None
        
        target_piece = qchess.board[target.x][target.y]

        #check direction of pawn (-1 is from bottom to top in this coordinate system)
        dy = +1
        if self.color == Color.WHITE:
            dy = -1

        if target.x == source.x:
            #only allow jumps to collapsed pawns or any entangle piece or null pieces
            #TODO: Implement when piece.collapsed is implemented
            # if target_piece != NullPiece and target_piece != self:
                # return Pawn.MoveType.INVALID, None

            if target.y == source.y + 2*dy:
                #double jump
                if self.has_moved:
                    return Pawn.MoveType.INVALID, None

                else:
                    return Pawn.MoveType.DOUBLE_STEP, None

            elif target.y == source.y + dy:
                return Pawn.MoveType.SINGLE_STEP, None

            else:
                return Pawn.MoveType.INVALID, None
        elif (
            (target.x == source.x + 1 or target.x == source.x - 1) and
            target.y == source.y + dy
        ):
            #en passant has priority
            if (qchess.ep_pawn_point and
                qchess.ep_pawn_point == Point(target.x, target.y - dy)
            ):
                return Pawn.MoveType.EN_PASSANT, Point(target.x, target.y - dy)

            elif target_piece != NullPiece and target_piece.color != self.color:
                return Pawn.MoveType.CAPTURE, None

            else:
                return Pawn.MoveType.INVALID, None

        else:
            return Pawn.MoveType.INVALID, None
 