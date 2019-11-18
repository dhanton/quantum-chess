import unittest

from qchess.board import *
from .quantum_test_engine import QuantumTestEngine

class TestSlideMove(unittest.TestCase):
    def test_nonclear_path_capture(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['Q', '0', '0'],
                ['0', 'k', '0'],
                ['0', '0', 'k'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['k', '0', '0'],
                ['0', '0', 'Q'],
            ],
            0.5
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.QUEEN, Color.WHITE))
            board.add_piece(2, 2, Piece(PieceType.KING, Color.BLACK))
            board.add_piece(1, 0, Piece(PieceType.KING, Color.BLACK))
            board.split_move(Point(1, 0), Point(1, 1), Point(0, 1))

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda board: board.standard_move(Point(0, 0), Point(2, 2)))
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    def test_blocked_move(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['Q', '0', '0'],
                ['0', '0', '0'],
                ['0', '0', 'K'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', '0', 'K'],
                ['0', '0', 'Q'],
            ],
            0.5
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.QUEEN, Color.WHITE))
            board.add_piece(1, 1, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(1, 1), Point(2, 2), Point(2, 1))
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda board: board.standard_move(Point(0, 0), Point(2, 2)))
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    def test_nonclear_path_same_piece_move(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['Q', '0', '0'],
                ['0', 'K', '0'],
                ['0', '0', 'Q'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['Q', '0', '0'],
                ['0', 'K', '0'],
                ['Q', '0', '0'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['0', '0', 'K'],
                ['0', '0', '0'],
                ['Q', '0', 'Q'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['Q', '0', 'K'],
                ['0', '0', '0'],
                ['0', '0', 'Q'],
            ],
            0.25
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.QUEEN, Color.WHITE))
            board.add_piece(1, 2, Piece(PieceType.QUEEN, Color.WHITE))
            board.add_piece(1, 0, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(1, 2), Point(0, 2), Point(2, 2))
            board.split_move(Point(1, 0), Point(1, 1), Point(2, 0))

        def action(board):
            board.standard_move(Point(0, 0), Point(2, 2))
            board.collapse_by_flag(None, collapse_all=True)
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    def test_nonclear_path_split_then_capture(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['Q', '0', '0'],
                ['0', 'K', '0'],
                ['0', '0', 'k'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['Q', 'K', 'K'],
                ['0', '0', 'k'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', '0', 'K'],
                ['0', '0', 'Q'],
            ],
            0.25
        )

        def board_factory(board):
            board.add_piece(1, 1, Piece(PieceType.QUEEN, Color.WHITE))
            board.split_move(Point(1, 1), Point(0, 0), Point(0, 1))
            board.add_piece(2, 0, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(2, 0), Point(2, 1), Point(1, 1))
            board.add_piece(2, 2, Piece(PieceType.KING, Color.BLACK))
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda board: board.standard_move(Point(0, 0), Point(2, 2)))
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    def test_nonclear_path_collapse_by_flag(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['Q', '0', '0', '0'],
                ['0', 'K', '0', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', '0', 'R'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['Q', '0', '0', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', 'K', '0'],
                ['0', '0', '0', 'R'],
            ],
            0.5
        )
        
        """
            When measuring the (3, 3) queen to move the rook,
            the King collapses even though the queen never could get past it.
            This is because their flags are combined, so when one collapses
            the other does too.
        """

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.QUEEN, Color.WHITE))
            board.add_piece(2, 1, Piece(PieceType.KING, Color.WHITE))
            board.add_piece(0, 3, Piece(PieceType.ROOK, Color.WHITE))
            board.split_move(Point(2, 1), Point(2, 2), Point(1, 1))
            board.standard_move(Point(0, 0), Point(3, 3))

        engine.set_board_factory(4, 4, board_factory)
        engine.set_action(lambda board: board.standard_move(Point(0, 3), Point(3, 3)))
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    def test_bell_state(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['N', '0', '0'],
                ['0', '0', '0'],
                ['0', 'K', 'b'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['N', '0', '0'],
                ['0', '0', '0'],
                ['0', '0', '0'],
            ],
            0.5
        )

        def board_factory(board):
            board.add_piece(1, 0, Piece(PieceType.KING, Color.WHITE))
            board.add_piece(1, 2, Piece(PieceType.KNIGHT, Color.WHITE))
            board.add_piece(2, 2, Piece(PieceType.BISHOP, Color.BLACK))
            
        def action(board):
            board.split_move(Point(1, 0), Point(1, 1), Point(0, 0))
            board.standard_move(Point(2, 2), Point(0, 0))
            board.standard_move(Point(1, 2), Point(0, 0))
            board.standard_move(Point(1, 1), Point(1, 2))
            board.collapse_by_flag(None, collapse_all=True)
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    def test_one_piece_triple_split_capture_entangle(self):
        engine = QuantumTestEngine()

        #we don't want to collapse because we want to 
        #make sure it's entangled properly
        engine.add_board_state(
            [
                ['b', '0', 'K', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', 'K', '0'],
                ['0', '0', '0', 'b'],
            ],
            1
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(0, 0), Point(2, 0), Point(2, 2), force=True)
            board.split_move(Point(2, 2), Point(0, 0), Point(2, 0), force=True)
            board.add_piece(3, 3, Piece(PieceType.BISHOP, Color.BLACK))
            
        engine.set_board_factory(4, 4, board_factory)
        engine.set_action(lambda board: board.standard_move(Point(3, 3), Point(0, 0)))
        engine.run_engine(100)
        engine.run_tests(self)

    def test_one_piece_triple_split_capture(self):
        engine = QuantumTestEngine()

        engine.add_board_state(
            [
                ['b', '0', 'K', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', '0', '0'],
            ],
            0.25
        )


        engine.add_board_state(
            [
                ['0', '0', '0', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', 'K', '0'],
                ['0', '0', '0', 'b'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['b', '0', '0', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', '0', '0'],
            ],
            0.25
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(0, 0), Point(2, 0), Point(2, 2), force=True)
            board.split_move(Point(2, 2), Point(0, 0), Point(2, 0), force=True)
            board.add_piece(3, 3, Piece(PieceType.BISHOP, Color.BLACK))

        def action(board):
            board.standard_move(Point(3, 3), Point(0, 0))
            board.collapse_by_flag(None, collapse_all=True)
            
        engine.set_board_factory(4, 4, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    def test_two_piece_triple_split_capture(self):
        engine = QuantumTestEngine()

        engine.add_board_state(
            [
                ['b', '0', 'K', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', '0', '0'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', 'K', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', 'K', '0'],
                ['0', '0', '0', 'b'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['K', '0', '0', '0'],
                ['0', '0', '0', '0'],
                ['0', '0', 'K', '0'],
                ['0', '0', '0', 'b'],
            ],
            0.25
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            board.add_piece(2, 2, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(0, 0), Point(2, 0), Point(2, 2), force=True)
            board.split_move(Point(2, 2), Point(0, 0), Point(2, 0), force=True)
            board.add_piece(3, 3, Piece(PieceType.BISHOP, Color.BLACK))

        engine.set_board_factory(4, 4, board_factory)
        engine.set_action(lambda board: board.standard_move(Point(3, 3), Point(0, 0)))
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)