from .engines.qiskit.qiskit_engine import QiskitEngine
from .point import Point
from .piece import *
from .pawn import Pawn

class QChess:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.board = [[NullPiece for y in range(height)] for x in range(width)]
        
        #holds the position of the captureable en passant pawn
        #none if the last move wasn't a pawn's double step
        self.ep_pawn_point = None
        self.just_moved_ep = False

        #default engine is QiskitEngine
        #TODO: Change engine from command line or Menubar
        self.engine = QiskitEngine(self, width, height)

    def perform_after_move(self):
        if self.just_moved_ep:
            self.just_moved_ep = False
        else:
            self.ep_pawn_point = None

    def in_bounds(self, x, y):
        if x < 0 or x >= self.width:
            return False
        
        if y < 0 or y >= self.height:
            return False

        return True

    def is_occupied(self, x, y):
        if self.board[x][y] != NullPiece:
            return True
        return False

    def get_array_index(self, x, y):
        return self.width * y + x

    def get_board_point(self, index):
        return Point(index%self.width, int(index/self.width))

    def get_piece(self, index):
        pos = self.get_board_point(index)
        return self.board[pos.x][pos.y]

    def add_piece(self, x, y, piece):
        if not self.in_bounds(x, y): return

        if self.is_occupied(x, y):
            print("add piece error - there is already a piece in that position")
            return

        self.board[x][y] = piece

        self.engine.on_add_piece(x, y, piece)

    def get_path_points(self, source, target):
        #not including source or target
        path = []
        
        if not self.in_bounds(source.x, source.y): return path 
        if not self.in_bounds(target.x, target.y): return path
        if source == target: return path

        vec = target - source
        if vec.x != 0 and vec.y != 0 and vec.x != vec.y: return path

        x_iter = y_iter = 0

        if vec.x != 0:
            x_iter = vec.x/abs(vec.x)
        if vec.y != 0:
            y_iter = vec.y/abs(vec.y)

        for i in range(1, max(abs(vec.x), abs(vec.y))):
            path.append(source + Point(x_iter * i, y_iter * i))

        return path

    def get_path_pieces(self, source, target):
        pieces = []

        for point in self.get_path_points(source, target):
            if self.board[point.x][point.y] != NullPiece:
                pieces.append(self.board[point.x][point.y])
        
        return pieces

    def ascii_render(self):
        s = ""

        for j in range(self.height):
            for i in range(self.width):
                piece = self.board[i][j]
                if piece:
                    s += piece.as_notation() + ' '
                else:
                    s += '0 '
            s += '\n'

        print(s)

    def get_simplified_matrix(self):
        m = []

        for j in range(self.height):
            row = []
            for i in range(self.width):
                row.append(self.board[i][j].as_notation())
            m.append(row)

        return m

    def standard_move(self, source, target, force=False):
        if not self.in_bounds(source.x, source.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(target.x, target.y):
            print('Invalid move - Target square not in bounds')
            return False
        
        if not self.is_occupied(source.x, source.y):
            print('Invalid move - Source square is empty')
            return False

        piece = self.board[source.x][source.y]

        if not force:
            if piece.type == PieceType.PAWN:
                move_type, ep_point = piece.is_move_valid(source, target, qchess=self)
                
                if move_type == Pawn.MoveType.INVALID:
                    print('Invalid move - Incorrect move for piece type pawn')
                    return False

            elif not piece.is_move_valid(source, target):
                print('Invalid move - Incorrect move for piece type ' + piece.type.name.lower())
                return False

        self.engine.standard_move(source, target, force=force)

        #update pawn information if move was succesful
        if piece.type == PieceType.PAWN and not piece.has_moved:
            piece.has_moved = True

            if move_type == Pawn.MoveType.DOUBLE_STEP:
                self.ep_pawn_point = target
                self.just_moved_ep = True

        return True

    def split_move(self, source, target1, target2, force=False):
        if not self.in_bounds(source.x, source.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(target1.x, target1.y) or not self.in_bounds(target2.x, target2.y):
            print('Invalid move - Target square not in bounds')
            return False
        
        if not self.is_occupied(source.x, source.y):
            print('Invalid move - Source square is empty')
            return False

        if target1 == target2:
            print("Invalid move - Both split targets are the same square")
            return False

        piece = self.board[source.x][source.y]

        if not force:
            if piece.type == PieceType.PAWN:
                print("Invalid move - Pawns can't perform split moves")
                return False

            if (
                not piece.is_move_valid(source, target1) or 
                not piece.is_move_valid(source, target2)
            ):
                print('Invalid move - Incorrect move for piece type ' + piece.type.name.lower())
                return False

        target_piece1 = self.board[target1.x][target1.y]
        target_piece2 = self.board[target2.x][target2.y]

        if target_piece1 != NullPiece and target_piece1.type != piece.type:
            print("Invalid move - Target square is not empty")
            return False

        if target_piece2 != NullPiece and target_piece2.type != piece.type:
            print("Invalid move - Target square is not empty")
            return False

        self.engine.split_move(source, target1, target2)

        return True
    
    def merge_move(self, source1, source2, target, force=False):
        if not self.in_bounds(source1.x, source1.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(source2.x, source2.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(target.x, target.y):
            print('Invalid move - Target square not in bounds')
            return False

        if source1 == source2:
            print('Invalid move - Both merge sources are the same squares')
            return False
        
        piece1 = self.board[source1.x][source1.y]
        piece2 = self.board[source2.x][source2.y]

        if not force:
            if piece1.type == PieceType.PAWN or piece2.type == PieceType.PAWN:
                print("Invalid move - Pawns can't perform merge moves")
                return False

            if (
                not piece1.is_move_valid(source1, target) or 
                not piece2.is_move_valid(source2, target)
            ):
                print('Invalid move - Incorrect move for piece type ' + piece1.type.lower())
                return False

        if piece1 != piece2:
            print('Invalid move - Different type of merge source pieces')
            return False

        target_piece = self.board[target.x][target.y]

        if target_piece != NullPiece and target_piece.type != piece1.type:
            print('Invalid move - Target square is not empty')
            return False

        self.engine.merge_move(source1, source2, target)

        return True
