import unittest

from qchess.board import *
from .quantum_test_engine import QuantumTestEngine

class TestSlideSplitMergeMove(unittest.TestCase):
    def test_blocked_split(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['R', 'K', '0'],
                ['0', '0', '0'],
                ['0', '0', '0'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['0', 'K', '0'],
                ['0', '0', '0'],
                ['0', '0', 'R'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['K', '0', '0'],
                ['0', '0', 'R'],
            ],
            0.5
        )

        def board_factory(board):
            board.add_piece(0, 2, Piece(PieceType.ROOK, Color.WHITE))
            board.add_piece(1, 1, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(1, 1), Point(0, 1), Point(1, 0))

        def action(board):
            board.split_move(Point(0, 2), Point(0, 0), Point(2, 2))
            board.collapse_by_flag(None, collapse_all=True)

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    def test_blocked_merge(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['R', '0', '0'],
                ['K', '0', '0'],
                ['R', '0', '0'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', '0', '0'],
                ['R', 'K', 'R'],
            ],
            0.5
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.ROOK, Color.WHITE))
            board.add_piece(2, 2, Piece(PieceType.ROOK, Color.WHITE))
            board.add_piece(0, 2, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(0, 2), Point(0, 1), Point(1, 2))

        def action(board):
            board.merge_move(Point(0, 0), Point(2, 2), Point(0, 2))
            board.collapse_by_flag(None, collapse_all=True)

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    def test_split_both_paths_blocked_entangle(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['R', 'K', 'R'],
                ['K', '0', '0'],
                ['R', '0', '0'],
            ],
            1
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.ROOK, Color.WHITE))
            board.add_piece(1, 1, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(1, 1), Point(0, 1), Point(1, 0))
        
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda board: board.split_move(Point(0, 0), Point(2, 0), Point(0, 2)))
        engine.run_engine(100)
        engine.run_tests(self)

    def test_split_one_path_blocked_entangle(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', 'R'],
                ['K', 'K', '0'],
                ['R', '0', '0'],
            ],
            1
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.ROOK, Color.WHITE))
            board.add_piece(1, 2, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(1, 2), Point(1, 1), Point(0, 1))
        
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda board: board.split_move(Point(0, 0), Point(2, 0), Point(0, 2)))
        engine.run_engine(100)
        engine.run_tests(self)