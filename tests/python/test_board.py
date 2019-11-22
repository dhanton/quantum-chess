import unittest

from qchess.board import *

class TestPiece(unittest.TestCase):
    def test_equality(self):
        """
        We use different arrays to test that == works properly
        even when comparing different instances of equivalent pieces
        """
        pieces1 = []
        pieces2 = []

        for piece_type in PieceType:
            pieces1.append(Piece(piece_type, Color.WHITE))
            pieces1.append(Piece(piece_type, Color.BLACK))

        for piece_type in PieceType:
            pieces2.append(Piece(piece_type, Color.WHITE))
            pieces2.append(Piece(piece_type, Color.BLACK))

        for i, piece1 in enumerate(pieces1):
            for j, piece2 in enumerate(pieces2):
                if i == j:
                    self.assertEqual(piece1, piece2, msg=str(piece1) + ' == ' + str(piece2))
                else:
                    self.assertNotEqual(piece1, piece2, msg=str(piece1) + ' == ' + str(piece2))

    def test_as_notation(self):
        self.assertEqual(Piece(PieceType.PAWN, Color.BLACK).as_notation(), 'p')
        self.assertEqual(Piece(PieceType.PAWN, Color.WHITE).as_notation(), 'P')
        self.assertEqual(Piece(PieceType.KNIGHT, Color.BLACK).as_notation(), 'n')
        self.assertEqual(Piece(PieceType.KNIGHT, Color.WHITE).as_notation(), 'N')
        self.assertEqual(Piece(PieceType.BISHOP, Color.BLACK).as_notation(), 'b')
        self.assertEqual(Piece(PieceType.BISHOP, Color.WHITE).as_notation(), 'B')
        self.assertEqual(Piece(PieceType.ROOK, Color.BLACK).as_notation(), 'r')
        self.assertEqual(Piece(PieceType.ROOK, Color.WHITE).as_notation(), 'R')
        self.assertEqual(Piece(PieceType.QUEEN, Color.BLACK).as_notation(), 'q')
        self.assertEqual(Piece(PieceType.QUEEN, Color.WHITE).as_notation(), 'Q')
        self.assertEqual(Piece(PieceType.KING, Color.BLACK).as_notation(), 'k')
        self.assertEqual(Piece(PieceType.KING, Color.WHITE).as_notation(), 'K')
    
    def test_is_move_valid(self):
        #Board is 5x5 always
        #Every piece is always in the center
        source = Point(2, 2)

        moves = {}

        moves[PieceType.KING] = [
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
        ]

        moves[PieceType.KNIGHT] = [
            [0, 1, 0, 1, 0],
            [1, 0, 0, 0, 1],
            [0, 0, 0, 0, 0],
            [1, 0, 0, 0, 1],
            [0, 1, 0, 1, 0],
        ]

        moves[PieceType.ROOK] = [
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [1, 1, 0, 1, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
        ]

        moves[PieceType.BISHOP] = [
            [1, 0, 0, 0, 1],
            [0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0],
            [1, 0, 0, 0, 1],
        ]

        moves[PieceType.QUEEN] = [
            [1, 0, 1, 0, 1],
            [0, 1, 1, 1, 0],
            [1, 1, 0, 1, 1],
            [0, 1, 1, 1, 0],
            [1, 0, 1, 0, 1],
        ]

        for x in range(25):
            i = x%5
            j = int(x/5)
            target = Point(i, j)

            for t in PieceType:
                if not t in moves: continue
                msg = t.name + ' is_move_valid from ' + str(source) + ' to ' + str(target)
                self.assertEqual(Piece(t, Color.WHITE).is_move_valid(source, target), moves[t][j][i], msg=msg)

    def test_is_pawn_move_valid(self):
        # INVALID = 0,
        # SINGLE_STEP = 1,
        # DOUBLE_STEP = 2,
        # CAPTURE = 3,
        # EN_PASSANT = 4

        clear = [
            [0, 0, 2, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        white = [
            [0, 0, 2, 0, 0],
            [0, 3, 1, 3, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        black = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 3, 1, 3, 0],
            [0, 0, 2, 0, 0],
        ]

        clear_already_moved = [
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        en_passant = [
            [0, 0, 2, 0, 0],
            [0, 4, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]

        #different color pawns to check move direction works
        source = Point(2, 2)
        pawn1 = Pawn(Color.WHITE)
        pawn2 = Pawn(Color.BLACK)
        pawn3 = Pawn(Color.WHITE)
        pawn3.has_moved = True

        #clear board
        board1 = Board(5, 5)
        
        #board with multiple pieces to capture
        board2 = Board(5, 5)
        board2.add_piece(1, 1, Piece(PieceType.KING, Color.BLACK))
        board2.add_piece(3, 1, Piece(PieceType.KING, Color.BLACK))
        board2.add_piece(1, 3, Piece(PieceType.KING, Color.WHITE))
        board2.add_piece(3, 3, Piece(PieceType.KING, Color.WHITE))

        #board where one black pawn performs a double step (to test EP)
        board3 = Board(5, 5)
        board3.add_piece(source.x, source.y, pawn1)
        board3.add_piece(1, 0, Pawn(Color.BLACK))
        board3.standard_move(Point(1, 0), Point(1, 2))

        for x in range(25):
            i = x%5
            j = int(x/5)
            target = Point(i, j)

            #since the result is a tuple (move_type, EP_point) we need [0]
            #EP_point being None for most moves
            self.assertEqual(int(pawn1.is_move_valid(source, target, board=board1)[0]), clear[j][i])
            self.assertEqual(int(pawn1.is_move_valid(source, target, board=board2)[0]), white[j][i])
            self.assertEqual(int(pawn2.is_move_valid(source, target, board=board2)[0]), black[j][i])

            self.assertEqual(int(pawn3.is_move_valid(source, target, board=board1)[0]), clear_already_moved[j][i])

            self.assertEqual(int(pawn1.is_move_valid(source, target, board=board3)[0]), en_passant[j][i])

class TestBoard(unittest.TestCase):
    def test_classical_board(self):
        #test squared board
        board = Board(3, 3)
        self.assertEqual(board.classical_board[1][1], NullPiece)
        board.classical_board[0][2] = Piece(PieceType.KING, Color.BLACK)
        self.assertNotEqual(board.classical_board[0][2], NullPiece)
        
        with self.assertRaises(IndexError):
            board.classical_board[0][3]
            board.classical_board[3][0]
            board.classical_board[100][129]
            board.classical_board[-1][-100]

        #test rectangular board
        board = Board(5, 1)
        self.assertEqual(board.classical_board[4][0], NullPiece)
        board.classical_board[3][0] = Piece(PieceType.KING, Color.BLACK)
        self.assertNotEqual(board.classical_board[3][0], NullPiece)
        
        with self.assertRaises(IndexError):
            board.classical_board[0][1]
            board.classical_board[5][0]
            board.classical_board[100][129]
            board.classical_board[-1][-100]

    def test_in_bounds(self):
        #test squared board
        board = Board(3, 3)
        self.assertFalse(board.in_bounds(3, 3))
        self.assertFalse(board.in_bounds(124, 0))
        self.assertFalse(board.in_bounds(0, 124))
        self.assertTrue(board.in_bounds(0, 0))
        self.assertTrue(board.in_bounds(2, 2))

        #test rectangular board
        board = Board(5, 1)
        self.assertFalse(board.in_bounds(3, 3))
        self.assertFalse(board.in_bounds(124, 0))
        self.assertFalse(board.in_bounds(0, 124))
        self.assertTrue(board.in_bounds(0, 0))
        self.assertTrue(board.in_bounds(4, 0))

    def test_is_occupied(self):
        board = Board(2, 2)
        board.classical_board[0][0] = Piece(PieceType.KING, Color.BLACK)

        self.assertTrue(board.is_occupied(0, 0))
        self.assertFalse(board.is_occupied(0, 1))
        self.assertFalse(board.is_occupied(1, 0))
        self.assertFalse(board.is_occupied(1, 1))

    def test_get_array_index(self):
        #there are 12 qubits, indexed 0...11
        board = Board(3, 4)

        self.assertEqual(board.get_array_index(0, 0), 0)
        self.assertEqual(board.get_array_index(1, 0), 1)
        self.assertEqual(board.get_array_index(2, 0), 2)
        self.assertEqual(board.get_array_index(0, 1), 3)
        self.assertEqual(board.get_array_index(1, 1), 4)
        self.assertEqual(board.get_array_index(2, 1), 5)
        self.assertEqual(board.get_array_index(0, 2), 6)
        self.assertEqual(board.get_array_index(1, 2), 7)
        self.assertEqual(board.get_array_index(2, 2), 8)
        self.assertEqual(board.get_array_index(0, 3), 9)
        self.assertEqual(board.get_array_index(1, 3), 10)
        self.assertEqual(board.get_array_index(2, 3), 11)
        
    def test_get_board_point(self):
        board = Board(3, 4)

        self.assertEqual(board.get_board_point(0), Point(0, 0))
        self.assertEqual(board.get_board_point(1), Point(1, 0))
        self.assertEqual(board.get_board_point(2), Point(2, 0))
        self.assertEqual(board.get_board_point(3), Point(0, 1))
        self.assertEqual(board.get_board_point(4), Point(1, 1))
        self.assertEqual(board.get_board_point(5), Point(2, 1))
        self.assertEqual(board.get_board_point(6), Point(0, 2))
        self.assertEqual(board.get_board_point(7), Point(1, 2))
        self.assertEqual(board.get_board_point(9), Point(0, 3))
        self.assertEqual(board.get_board_point(10), Point(1, 3))
        self.assertEqual(board.get_board_point(11), Point(2, 3))

    def test_simplified_matrix(self):
        board = Board(3, 3)
        board.add_piece(1, 0, Piece(PieceType.BISHOP, Color.BLACK))
        board.add_piece(1, 1, Piece(PieceType.KING, Color.WHITE))
        board.add_piece(2, 1, Piece(PieceType.PAWN, Color.WHITE))
        board.add_piece(0, 2, Piece(PieceType.QUEEN, Color.BLACK))

        result = [
            ['0', 'b', '0'],
            ['0', 'K', 'P'],
            ['q', '0', '0'],
        ]
        
        self.assertEqual(board.get_simplified_matrix(), result)

    def test_path_points(self):
        diagonal = [Point(1, 1), Point(2, 2), Point(3, 3)]
        diagonal_inv = [Point(3, 3), Point(2, 2), Point(1, 1)]
        row = [Point(1, 0), Point(2, 0), Point(3, 0)]
        row_inv = [Point(3, 0), Point(2, 0), Point(1, 0)]
        col = [Point(0, 1), Point(0, 2), Point(0, 3)]
        col_inv = [Point(0, 3), Point(0, 2), Point(0, 1)]

        board = Board(5, 5)
        self.assertEqual(board.get_path_points(Point(0, 0), Point(4, 4)), diagonal)
        self.assertEqual(board.get_path_points(Point(0, 0), Point(0, 4)), col)
        self.assertEqual(board.get_path_points(Point(0, 0), Point(4, 0)), row)
        self.assertEqual(board.get_path_points(Point(4, 4), Point(0, 0)), diagonal_inv)
        self.assertEqual(board.get_path_points(Point(0, 4), Point(0, 0)), col_inv)
        self.assertEqual(board.get_path_points(Point(4, 0), Point(0, 0)), row_inv)
