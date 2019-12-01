import unittest

from qchess.quantum_chess import *
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

        def board_factory(qchess):
            qchess.add_piece(1, 2, Pawn(Color.WHITE))
            qchess.add_piece(0, 1, Piece(PieceType.KNIGHT, Color.BLACK))
            
        def action(qchess):
            qchess.standard_move(Point(1, 2), Point(0, 1))
            qchess.engine.collapse_all()
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(100)
        engine.run_tests(self)

    def test_capture_split_piece(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['p', '0', '0'],
                ['0', '0', 'K'],
                ['0', '0', '0'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', '0'],
                ['0', 'p', '0'],
                ['0', '0', '0'],
            ],
            0.5
        )

        def board_factory(qchess):
            qchess.add_piece(0, 0, Pawn(Color.BLACK))
            qchess.add_piece(1, 2, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(1, 2), Point(1, 1), Point(2, 1))
            
        #we don't use collapse_all here since we want to make sure the pawn collapses the king properly    
        
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(lambda qchess: qchess.standard_move(Point(0, 0), Point(1, 1)))
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

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

        def board_factory(qchess):
            qchess.add_piece(2, 2, Pawn(Color.WHITE))
            qchess.add_piece(1, 0, Pawn(Color.BLACK))
            qchess.standard_move(Point(1, 0), Point(1, 2))
            
        def action(qchess):
            qchess.standard_move(Point(2, 2), Point(1, 1))
            qchess.engine.collapse_all()
            
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

        def board_factory(qchess):
            qchess.add_piece(2, 2, Pawn(Color.WHITE))
            qchess.add_piece(1, 0, Pawn(Color.BLACK))
            qchess.add_piece(0, 0, Piece(PieceType.KING, Color.BLACK))
            qchess.split_move(Point(0, 0), Point(1, 1), Point(0, 1))
            qchess.standard_move(Point(1, 0), Point(1, 2))
            
        def action(qchess):
            qchess.standard_move(Point(2, 2), Point(1, 1))
            qchess.engine.collapse_all()
            
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

        def board_factory(qchess):
            qchess.add_piece(2, 2, Pawn(Color.WHITE))
            qchess.add_piece(1, 0, Pawn(Color.BLACK))
            qchess.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(1, 1), Point(0, 1))
            qchess.standard_move(Point(1, 0), Point(1, 2))
            
        def action(qchess):
            qchess.standard_move(Point(2, 2), Point(1, 1))
            
        engine.set_board_factory(3, 3, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)
