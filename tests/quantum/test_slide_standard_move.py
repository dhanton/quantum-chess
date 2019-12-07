import unittest

#import shots and delta default values
from . import *

from qchess.quantum_chess import *
from .quantum_test_engine import QuantumTestEngine

class TestSlideStandardMove(unittest.TestCase):
    def test_nonclear_path_capture(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['Q', '0', '0'],
                ['0', 'k', '0'],
                ['0', '0', 'n'],
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

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.QUEEN, Color.WHITE))
            qchess.add_piece(2, 2, Piece(PieceType.KNIGHT, Color.BLACK))
            qchess.add_piece(1, 0, Piece(PieceType.KING, Color.BLACK))
            qchess.split_move(Point(1, 0), Point(1, 1), Point(0, 1))

        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda qchess: qchess.standard_move(Point(0, 0), Point(2, 2)))
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

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

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.QUEEN, Color.WHITE))
            qchess.add_piece(1, 1, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(1, 1), Point(2, 2), Point(2, 1))
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda qchess: qchess.standard_move(Point(0, 0), Point(2, 2)))
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

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

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.QUEEN, Color.WHITE))
            qchess.add_piece(1, 2, Piece(PieceType.QUEEN, Color.WHITE))
            qchess.add_piece(1, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(1, 2), Point(0, 2), Point(2, 2))
            qchess.split_move(Point(1, 0), Point(1, 1), Point(2, 0))

        def action(qchess):
            qchess.standard_move(Point(0, 0), Point(2, 2))
            qchess.engine.collapse_all()
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

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

        def board_factory(qchess):
            qchess.add_piece(1, 1, Piece(PieceType.QUEEN, Color.WHITE))
            qchess.split_move(Point(1, 1), Point(0, 0), Point(0, 1))
            qchess.add_piece(2, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(2, 0), Point(2, 1), Point(1, 1))
            qchess.add_piece(2, 2, Piece(PieceType.KING, Color.BLACK))
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda qchess: qchess.standard_move(Point(0, 0), Point(2, 2)))
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

    def test_nonclear_path_collapse(self):
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
            Even though the queen can never get past the kings, they are still entangled,
            and the queen is shown in the target position as well. This is because
            QiskitEngine avoids simulating quantum states and only gets the same info it
            would from a real quantum computer.

            So the engine doesn't know that, even though the kings are split,
            the path is always blocked. Because the kings are split it assumes
            there is a posibility the path is clear and the queen is in the target position.
        """

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.QUEEN, Color.WHITE))
            qchess.add_piece(2, 1, Piece(PieceType.KING, Color.WHITE))
            qchess.add_piece(0, 3, Piece(PieceType.ROOK, Color.WHITE))
            qchess.split_move(Point(2, 1), Point(2, 2), Point(1, 1))
            qchess.standard_move(Point(0, 0), Point(3, 3))

        engine.set_board_factory(4, 4, board_factory)
        engine.set_action(lambda qchess: qchess.standard_move(Point(0, 3), Point(3, 3)))
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

    def test_bell_state_entangle(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['N', '0', '0'],
                ['0', '0', '0'],
                ['0', 'K', 'b'],
            ],
            1
        )

        def board_factory(qchess):
            qchess.add_piece(1, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.add_piece(1, 2, Piece(PieceType.KNIGHT, Color.WHITE))
            qchess.add_piece(2, 2, Piece(PieceType.BISHOP, Color.BLACK))
            
        def action(qchess):
            qchess.split_move(Point(1, 0), Point(1, 1), Point(0, 0))
            qchess.standard_move(Point(2, 2), Point(0, 0))
            qchess.standard_move(Point(1, 2), Point(0, 0))
            qchess.standard_move(Point(1, 1), Point(1, 2))
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(entangle_shots)
        engine.run_tests(self, delta=entangle_delta)

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

        def board_factory(qchess):
            qchess.add_piece(1, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.add_piece(1, 2, Piece(PieceType.KNIGHT, Color.WHITE))
            qchess.add_piece(2, 2, Piece(PieceType.BISHOP, Color.BLACK))
            
        def action(qchess):
            qchess.split_move(Point(1, 0), Point(1, 1), Point(0, 0))
            qchess.standard_move(Point(2, 2), Point(0, 0))
            qchess.standard_move(Point(1, 2), Point(0, 0))
            qchess.standard_move(Point(1, 1), Point(1, 2))
            qchess.engine.collapse_all()
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

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

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(2, 0), Point(2, 2), force=True)
            qchess.split_move(Point(2, 2), Point(0, 0), Point(2, 0), force=True)
            qchess.add_piece(3, 3, Piece(PieceType.BISHOP, Color.BLACK))
            
        engine.set_board_factory(4, 4, board_factory)
        engine.set_action(lambda qchess: qchess.standard_move(Point(3, 3), Point(0, 0)))
        engine.run_engine(entangle_shots)
        engine.run_tests(self, delta=entangle_delta)

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

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(2, 0), Point(2, 2), force=True)
            qchess.split_move(Point(2, 2), Point(0, 0), Point(2, 0), force=True)
            qchess.add_piece(3, 3, Piece(PieceType.BISHOP, Color.BLACK))

        def action(qchess):
            qchess.standard_move(Point(3, 3), Point(0, 0))
            qchess.engine.collapse_all()
            
        engine.set_board_factory(4, 4, board_factory)
        engine.set_action(action)
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)

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

        def board_factory(qchess):
            qchess.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.add_piece(2, 2, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(2, 0), Point(2, 2), force=True)
            qchess.split_move(Point(2, 2), Point(0, 0), Point(2, 0), force=True)
            qchess.add_piece(3, 3, Piece(PieceType.BISHOP, Color.BLACK))

        engine.set_board_factory(4, 4, board_factory)
        engine.set_action(lambda qchess: qchess.standard_move(Point(3, 3), Point(0, 0)))
        engine.run_engine(standard_shots)
        engine.run_tests(self, delta=standard_delta)