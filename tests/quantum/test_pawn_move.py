import unittest

from qchess.board import *
from .quantum_test_engine import QuantumTestEngine

class TestPawnMove(unittest.TestCase):
    def test_capture(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['P', '0', '0'],
                ['0', '0', '0'],
            ],
            1
        )

        def board_factory(board):
            board.add_piece(1, 2, Pawn(Color.WHITE))
            board.add_piece(0, 1, Piece(PieceType.KNIGHT, Color.BLACK))
            
        def action(board):
            board.standard_move(Point(1, 2), Point(0, 1))
            board.collapse_by_flag(None, collapse_all=True)
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(100)
        engine.run_tests(self)

    def test_en_passant(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', 'P', '0'],
                ['0', '0', '0'],
            ],
            1
        )

        def board_factory(board):
            board.add_piece(2, 2, Pawn(Color.WHITE))
            board.add_piece(1, 0, Pawn(Color.BLACK))
            board.standard_move(Point(1, 0), Point(1, 2))
            
        def action(board):
            board.standard_move(Point(2, 2), Point(1, 1))
            board.collapse_by_flag(None, collapse_all=True)
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(100)
        engine.run_tests(self)

    def test_capture_en_passant(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', 'p', '0'],
                ['0', 'P', '0'],
                ['0', '0', '0'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['k', 'P', '0'],
                ['0', '0', '0'],
            ],
            0.5
        )

        def board_factory(board):
            board.add_piece(2, 2, Pawn(Color.WHITE))
            board.add_piece(1, 0, Pawn(Color.BLACK))
            board.add_piece(0, 0, Piece(PieceType.KING, Color.BLACK))
            board.split_move(Point(0, 0), Point(1, 1), Point(0, 1))
            board.standard_move(Point(1, 0), Point(1, 2))
            
        def action(board):
            board.standard_move(Point(2, 2), Point(1, 1))
            board.collapse_by_flag(None, collapse_all=True)
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    def test_blocked_en_passant(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', 'p', '0'],
                ['0', 'K', '0'],
                ['0', '0', 'P'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['K', 'P', '0'],
                ['0', '0', '0'],
            ],
            0.5
        )

        def board_factory(board):
            board.add_piece(2, 2, Pawn(Color.WHITE))
            board.add_piece(1, 0, Pawn(Color.BLACK))
            board.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(0, 0), Point(1, 1), Point(0, 1))
            board.standard_move(Point(1, 0), Point(1, 2))
            
        def action(board):
            board.standard_move(Point(2, 2), Point(1, 1))
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)