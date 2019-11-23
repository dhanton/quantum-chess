import unittest

from qchess.quantum_chess import *

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
        qchess1 = QChess(5, 5)
        
        #board with multiple pieces to capture
        qchess2 = QChess(5, 5)
        qchess2.add_piece(1, 1, Piece(PieceType.KING, Color.BLACK))
        qchess2.add_piece(3, 1, Piece(PieceType.KING, Color.BLACK))
        qchess2.add_piece(1, 3, Piece(PieceType.KING, Color.WHITE))
        qchess2.add_piece(3, 3, Piece(PieceType.KING, Color.WHITE))

        #board where one black pawn performs a double step (to test EP)
        qchess3 = QChess(5, 5)
        qchess3.add_piece(source.x, source.y, pawn1)
        qchess3.add_piece(1, 0, Pawn(Color.BLACK))
        qchess3.standard_move(Point(1, 0), Point(1, 2))

        for x in range(25):
            i = x%5
            j = int(x/5)
            target = Point(i, j)

            #since the result is a tuple (move_type, EP_point) we need [0]
            #EP_point being None for most moves
            self.assertEqual(int(pawn1.is_move_valid(source, target, qchess=qchess1)[0]), clear[j][i])
            self.assertEqual(int(pawn1.is_move_valid(source, target, qchess=qchess2)[0]), white[j][i])
            self.assertEqual(int(pawn2.is_move_valid(source, target, qchess=qchess2)[0]), black[j][i])

            self.assertEqual(int(pawn3.is_move_valid(source, target, qchess=qchess1)[0]), clear_already_moved[j][i])

            self.assertEqual(int(pawn1.is_move_valid(source, target, qchess=qchess3)[0]), en_passant[j][i])

class TestClassicalBoard(unittest.TestCase):
    def test_classical_qboard(self):
        #test squared qboard
        qchess = QChess(3, 3)
        self.assertEqual(qchess.board[1][1], NullPiece)
        qchess.board[0][2] = Piece(PieceType.KING, Color.BLACK)
        self.assertNotEqual(qchess.board[0][2], NullPiece)
        
        with self.assertRaises(IndexError):
            qchess.board[0][3]
            qchess.board[3][0]
            qchess.board[100][129]
            qchess.board[-1][-100]

        #test rectangular board
        qchess = QChess(5, 1)
        self.assertEqual(qchess.board[4][0], NullPiece)
        qchess.board[3][0] = Piece(PieceType.KING, Color.BLACK)
        self.assertNotEqual(qchess.board[3][0], NullPiece)
        
        with self.assertRaises(IndexError):
            qchess.board[0][1]
            qchess.board[5][0]
            qchess.board[100][129]
            qchess.board[-1][-100]

    def test_in_bounds(self):
        #test squared board
        qchess = QChess(3, 3)
        self.assertFalse(qchess.in_bounds(3, 3))
        self.assertFalse(qchess.in_bounds(124, 0))
        self.assertFalse(qchess.in_bounds(0, 124))
        self.assertTrue(qchess.in_bounds(0, 0))
        self.assertTrue(qchess.in_bounds(2, 2))

        #test rectangular board
        qchess = QChess(5, 1)
        self.assertFalse(qchess.in_bounds(3, 3))
        self.assertFalse(qchess.in_bounds(124, 0))
        self.assertFalse(qchess.in_bounds(0, 124))
        self.assertTrue(qchess.in_bounds(0, 0))
        self.assertTrue(qchess.in_bounds(4, 0))

    def test_is_occupied(self):
        qchess = QChess(2, 2)
        qchess.board[0][0] = Piece(PieceType.KING, Color.BLACK)

        self.assertTrue(qchess.is_occupied(0, 0))
        self.assertFalse(qchess.is_occupied(0, 1))
        self.assertFalse(qchess.is_occupied(1, 0))
        self.assertFalse(qchess.is_occupied(1, 1))

    def test_get_array_index(self):
        #there are 12 qubits, indexed 0...11
        qchess = QChess(3, 4)

        self.assertEqual(qchess.get_array_index(0, 0), 0)
        self.assertEqual(qchess.get_array_index(1, 0), 1)
        self.assertEqual(qchess.get_array_index(2, 0), 2)
        self.assertEqual(qchess.get_array_index(0, 1), 3)
        self.assertEqual(qchess.get_array_index(1, 1), 4)
        self.assertEqual(qchess.get_array_index(2, 1), 5)
        self.assertEqual(qchess.get_array_index(0, 2), 6)
        self.assertEqual(qchess.get_array_index(1, 2), 7)
        self.assertEqual(qchess.get_array_index(2, 2), 8)
        self.assertEqual(qchess.get_array_index(0, 3), 9)
        self.assertEqual(qchess.get_array_index(1, 3), 10)
        self.assertEqual(qchess.get_array_index(2, 3), 11)
        
    def test_get_board_point(self):
        qchess = QChess(3, 4)

        self.assertEqual(qchess.get_board_point(0), Point(0, 0))
        self.assertEqual(qchess.get_board_point(1), Point(1, 0))
        self.assertEqual(qchess.get_board_point(2), Point(2, 0))
        self.assertEqual(qchess.get_board_point(3), Point(0, 1))
        self.assertEqual(qchess.get_board_point(4), Point(1, 1))
        self.assertEqual(qchess.get_board_point(5), Point(2, 1))
        self.assertEqual(qchess.get_board_point(6), Point(0, 2))
        self.assertEqual(qchess.get_board_point(7), Point(1, 2))
        self.assertEqual(qchess.get_board_point(9), Point(0, 3))
        self.assertEqual(qchess.get_board_point(10), Point(1, 3))
        self.assertEqual(qchess.get_board_point(11), Point(2, 3))

    def test_simplified_matrix(self):
        qchess = QChess(3, 3)
        qchess.add_piece(1, 0, Piece(PieceType.BISHOP, Color.BLACK))
        qchess.add_piece(1, 1, Piece(PieceType.KING, Color.WHITE))
        qchess.add_piece(2, 1, Piece(PieceType.PAWN, Color.WHITE))
        qchess.add_piece(0, 2, Piece(PieceType.QUEEN, Color.BLACK))

        result = [
            ['0', 'b', '0'],
            ['0', 'K', 'P'],
            ['q', '0', '0'],
        ]
        
        self.assertEqual(qchess.get_simplified_matrix(), result)

    def test_path_points(self):
        diagonal = [Point(1, 1), Point(2, 2), Point(3, 3)]
        diagonal_inv = [Point(3, 3), Point(2, 2), Point(1, 1)]
        row = [Point(1, 0), Point(2, 0), Point(3, 0)]
        row_inv = [Point(3, 0), Point(2, 0), Point(1, 0)]
        col = [Point(0, 1), Point(0, 2), Point(0, 3)]
        col_inv = [Point(0, 3), Point(0, 2), Point(0, 1)]

        qchess = QChess(5, 5)
        self.assertEqual(qchess.get_path_points(Point(0, 0), Point(4, 4)), diagonal)
        self.assertEqual(qchess.get_path_points(Point(0, 0), Point(0, 4)), col)
        self.assertEqual(qchess.get_path_points(Point(0, 0), Point(4, 0)), row)
        self.assertEqual(qchess.get_path_points(Point(4, 4), Point(0, 0)), diagonal_inv)
        self.assertEqual(qchess.get_path_points(Point(0, 4), Point(0, 0)), col_inv)
        self.assertEqual(qchess.get_path_points(Point(4, 0), Point(0, 0)), row_inv)
