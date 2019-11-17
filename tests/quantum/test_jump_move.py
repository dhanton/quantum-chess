import unittest

from qchess.board import *
from .quantum_test_engine import QuantumTestEngine

class TestJumpMove(unittest.TestCase):
    def test_split_move(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', 'K', '0'],
                ['K', '0', '0'],
                ['0', '0', '0'],
            ],
            1
        )

        engine.set_board_factory(3, 3, lambda board: board.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE)))
        engine.set_action(lambda board: board.split_move(Point(0, 0), Point(1, 0), Point(0, 1)))
        engine.run_engine(100)
        engine.run_tests(self)

    def test_merge_move(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', 'K', '0'],
                ['0', '0', '0'],
            ],
            1
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(0, 0), Point(1, 0), Point(0, 1))

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda board: board.merge_move(Point(0, 1), Point(1, 0), Point(1, 1)))
        engine.run_engine(100)
        engine.run_tests(self)


    def test_capture_move(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['K', '0', '0'],
                ['0', 'k', '0'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', '0', '0'],
                ['0', 'K', '0'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', '0', 'K'],
                ['0', 'k', '0'],
            ],
            0.25
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(0, 0), Point(1, 0), Point(0, 1))
            board.split_move(Point(1, 0), Point(1, 1), Point(2, 1))
            board.add_piece(1, 2, Piece(PieceType.KING, Color.BLACK))

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda board: board.standard_move(Point(1, 1), Point(1, 2)))
        engine.run_engine(500)
        engine.run_tests(self, delta=0.05)

    def test_blocked_move(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['P', 'K', '0'],
                ['0', '0', '0'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', 'K', 'P'],
                ['0', '0', '0'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', 'P', '0'],
                ['0', 'K', '0'],
            ],
            0.25
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.PAWN, Color.WHITE))
            board.split_move(Point(0, 0), Point(1, 0), Point(0, 1), force=True)
            board.split_move(Point(1, 0), Point(1, 1), Point(2, 1), force=True)
            board.add_piece(1, 2, Piece(PieceType.KING, Color.WHITE))

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda board: board.standard_move(Point(1, 2), Point(1, 1)))
        engine.run_engine(500)
        engine.run_tests(self, delta=0.05)

    def test_standard_move_to_split(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['K', 'K', '0'],
                ['0', '0', '0'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', 'K', '0'],
                ['K', '0', '0'],
            ],
            0.5
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            board.add_piece(0, 2, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(0, 0), Point(0, 1), Point(1, 1))

        def action(board):
            board.standard_move(Point(0, 2), Point(1, 1))
            board.collapse_by_flag(1)

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.05)

    def test_merge_of_piece_and_split(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', 'K', '0'],
                ['0', '0', '0'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', 'K', '0'],
                ['0', 'K', '0'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', '0', '0'],
                ['0', 'K', '0'],
            ],
            0.5
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            board.add_piece(0, 2, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(0, 0), Point(0, 1), Point(1, 1))

        def action(board):
            board.merge_move(Point(0, 1), Point(0, 2), Point(1, 2))
            board.collapse_by_flag(0xfffff)

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.05)

    def test_split_to_piece(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['K', '0', '0'],
                ['K', '0', '0'],
                ['0', '0', '0'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['K', '0', '0'],
                ['0', 'K', '0'],
                ['0', '0', '0'],
            ],
            0.5
        )

        def board_factory(board):
            board.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            board.add_piece(1, 1, Piece(PieceType.KING, Color.WHITE))
            board.split_move(Point(0, 0), Point(0, 1), Point(1, 1))

        def action(board):
            board.collapse_by_flag(0xfffff)

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.05)