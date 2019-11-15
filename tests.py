import unittest

from board import *

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

        for x in range(25):
            i = x%5
            j = int(x/5)
            target = Point(i, j)

            for t in PieceType:
                if not t in moves: continue
                self.assertEqual(Piece(t, Color.WHITE).is_move_valid(source, target), moves[t][i][j])

class TestBoard(unittest.TestCase):
    def test_classical_board(self):
        #test squared board
        board = Board(3, 3)
        self.assertEqual(board.classical_board[1][1], NullPiece)
        board.classical_board[0][2] = Piece(PieceType.KING, Color.BLACK)
        self.assertTrue(board.classical_board[0][2])
        
        with self.assertRaises(IndexError):
            board.classical_board[0][3]
            board.classical_board[3][0]
            board.classical_board[100][129]
            board.classical_board[-1][-100]

        #test rectangular board
        board = Board(5, 1)
        self.assertEqual(board.classical_board[4][0], NullPiece)
        board.classical_board[3][0] = Piece(PieceType.KING, Color.BLACK)
        self.assertTrue(board.classical_board[3][0])
        
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

    def test_get_qubit_index(self):
        #there are 9 qubits, indexed 0...8
        board = Board(3, 3)

        self.assertIs(board.get_qubit_index(0, 0), 0)
        self.assertIs(board.get_qubit_index(1, 0), 1)
        self.assertIs(board.get_qubit_index(2, 0), 2)
        self.assertIs(board.get_qubit_index(0, 1), 3)
        self.assertIs(board.get_qubit_index(1, 1), 4)
        self.assertIs(board.get_qubit_index(2, 1), 5)
        self.assertIs(board.get_qubit_index(0, 2), 6)
        self.assertIs(board.get_qubit_index(1, 2), 7)
        self.assertIs(board.get_qubit_index(2, 2), 8)
        

if __name__ == "__main__":
    unittest.main()