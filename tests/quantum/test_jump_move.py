import unittest

#import shots and delta default values
from . import *

from qchess.quantum_chess import *
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

        engine.set_board_factory(3, 3, lambda qchess: qchess.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE)))
        engine.set_action(lambda qchess: qchess.split_move(Point(0, 0), Point(1, 0), Point(0, 1)))
        engine.run_engine(entangle_shots)
        engine.run_tests(self, delta=entangle_delta)

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

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(1, 0), Point(0, 1))

        def action(qchess):
            qchess.merge_move(Point(0, 1), Point(1, 0), Point(1, 1))
            qchess.engine.collapse_all()

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(entangle_shots)
        engine.run_tests(self, delta=entangle_delta)


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

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(1, 0), Point(0, 1))
            qchess.split_move(Point(1, 0), Point(1, 1), Point(2, 1))
            qchess.add_piece(1, 2, Piece(PieceType.KING, Color.BLACK))

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda qchess: qchess.standard_move(Point(1, 1), Point(1, 2)))
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

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

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.PAWN, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(1, 0), Point(0, 1), force=True)
            qchess.split_move(Point(1, 0), Point(1, 1), Point(2, 1), force=True)
            qchess.add_piece(1, 2, Piece(PieceType.KING, Color.WHITE))

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda qchess: qchess.standard_move(Point(1, 2), Point(1, 1)))
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

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

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.add_piece(0, 2, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(0, 1), Point(1, 1))

        def action(qchess):
            qchess.standard_move(Point(0, 2), Point(1, 1))
            qchess.engine.collapse_all()

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

    def test_double_split_merge(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', 'K'],
                ['0', '0', '0'],
                ['0', '0', '0'],
            ],
            0.25
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', '0', 'K'],
                ['0', '0', '0'],
            ],
            0.375
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', '0', '0'],
                ['0', '0', 'K'],
            ],
            0.375
        )

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(1, 0), Point(1, 1))
            qchess.split_move(Point(1, 0), Point(2, 0), Point(2, 1))

        def action(qchess):
            qchess.merge_move(Point(2, 1), Point(1, 1), Point(2, 2))
            qchess.engine.collapse_all()

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

    def test_two_piece_single_split_merge(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['K', 'K', '0'],
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
                ['K', '0', '0'],
                ['0', 'K', '0'],
            ],
            0.5
        )

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.add_piece(0, 2, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(0, 1), Point(1, 1))

        def action(qchess):
            qchess.merge_move(Point(0, 1), Point(0, 2), Point(1, 2))
            qchess.engine.collapse_all()

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

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

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.add_piece(1, 1, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(0, 1), Point(1, 1))

        def action(qchess):
            qchess.engine.collapse_all()

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

    def test_merge_proper_capture_collapse(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', 'K', '0'],
                ['0', '0', '0'],
                ['0', '0', 'K'],
            ],
            0.25
        )
        
        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', 'K', '0'],
                ['0', '0', '0'],
                ['0', 'K', '0'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', 'k', '0'],
                ['0', '0', '0'],
                ['0', 'K', 'K'],
            ],
            0.25
        )

        def board_factory(qchess):
            qchess.add_piece(1, 1, Piece(PieceType.KING, Color.BLACK))
            qchess.add_piece(1, 2, Piece(PieceType.KING, Color.WHITE))
            qchess.add_piece(2, 2, Piece(PieceType.KING, Color.WHITE))

            qchess.split_move(Point(1, 2), Point(1, 3), Point(2, 3))
            qchess.merge_move(Point(1, 3), Point(2, 2), Point(1, 2))

        def action(qchess):
            qchess.standard_move(Point(1, 2), Point(1, 1))

        engine.set_board_factory(3, 4, board_factory)
        engine.set_action(action)
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)
