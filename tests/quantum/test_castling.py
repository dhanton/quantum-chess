import unittest

from qchess.quantum_chess import *
from .quantum_test_engine import QuantumTestEngine

class TestCastling(unittest.TestCase):
    def test_target_blocking(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0', '0', '0'],
                ['R', '0', 'Q', '0', 'K'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', 'Q', '0', '0'],
                ['0', '0', 'K', 'R', '0'],
            ],
            0.5
        )

        def board_factory(qchess):
            castling_type = {}
            castling_type['rook_start_square'] = Point(0, 1)
            castling_type['rook_end_square'] = Point(3, 1)
            castling_type['king_start_square'] = Point(4, 1)
            castling_type['king_end_square'] = Point(2, 1)

            qchess.castling_types.append(castling_type)

            qchess.add_piece(0, 1, Piece(PieceType.ROOK, Color.WHITE))
            qchess.add_piece(4, 1, Piece(PieceType.KING, Color.WHITE))

            qchess.add_piece(1, 0, Piece(PieceType.QUEEN, Color.WHITE))
            qchess.split_move(Point(1, 0), Point(2, 0), Point(2, 1))

        engine.set_board_factory(5, 2, board_factory)
        engine.set_action(lambda qchess: qchess.standard_move(Point(4, 1), Point(2, 1)))
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    def test_straight_path_blocking_entangle(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', 'Q', '0', '0', '0'],
                ['R', 'Q', 'K', 'R', 'K'],
            ],
            1
        )

        def board_factory(qchess):
            castling_type = {}
            castling_type['rook_start_square'] = Point(0, 1)
            castling_type['rook_end_square'] = Point(3, 1)
            castling_type['king_start_square'] = Point(4, 1)
            castling_type['king_end_square'] = Point(2, 1)

            qchess.castling_types.append(castling_type)

            qchess.add_piece(0, 1, Piece(PieceType.ROOK, Color.WHITE))
            qchess.add_piece(4, 1, Piece(PieceType.KING, Color.WHITE))

            qchess.add_piece(0, 0, Piece(PieceType.QUEEN, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(1, 0), Point(1, 1))

        engine.set_board_factory(5, 2, board_factory)
        engine.set_action(lambda qchess: qchess.standard_move(Point(4, 1), Point(2, 1)))
        engine.run_engine(100)
        engine.run_tests(self)

    def test_straight_path_blocking(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0', '0', '0'],
                ['R', 'Q', '0', '0', 'K'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', 'Q', '0', '0', '0'],
                ['0', '0', 'K', 'R', '0'],
            ],
            0.5
        )

        def board_factory(qchess):
            castling_type = {}
            castling_type['rook_start_square'] = Point(0, 1)
            castling_type['rook_end_square'] = Point(3, 1)
            castling_type['king_start_square'] = Point(4, 1)
            castling_type['king_end_square'] = Point(2, 1)

            qchess.castling_types.append(castling_type)

            qchess.add_piece(0, 1, Piece(PieceType.ROOK, Color.WHITE))
            qchess.add_piece(4, 1, Piece(PieceType.KING, Color.WHITE))

            qchess.add_piece(0, 0, Piece(PieceType.QUEEN, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(1, 0), Point(1, 1))

        def action(qchess):
            qchess.standard_move(Point(4, 1), Point(2, 1))
            qchess.engine.collapse_all()

        engine.set_board_factory(5, 2, board_factory)
        engine.set_action(action)
        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)

    #I'm not sure which game mode would ever need something like this
    #but you can castle diagonally
    def test_diagonal_path_blocking(self):
        engine = QuantumTestEngine()
        engine.add_board_state(
            [
                ['0', '0', '0', '0', '0', '0'],
                ['0', 'Q', '0', '0', '0', '0'],
                ['K', '0', '0', '0', '0', 'R'],
            ],
            0.5
        )

        engine.add_board_state(
            [
                ['0', '0', 'K', 'R', '0', '0'],
                ['Q', '0', '0', '0', '0', '0'],
                ['0', '0', '0', '0', '0', '0'],
            ],
            0.5
        )

        def board_factory(qchess):
            castling_type = {}
            castling_type['rook_start_square'] = Point(5, 2)
            castling_type['rook_end_square'] = Point(3, 0)
            castling_type['king_start_square'] = Point(0, 2)
            castling_type['king_end_square'] = Point(2, 0)

            qchess.castling_types.append(castling_type)

            qchess.add_piece(5, 2, Piece(PieceType.ROOK, Color.WHITE))
            qchess.add_piece(0, 2, Piece(PieceType.KING, Color.WHITE))

            qchess.add_piece(0, 0, Piece(PieceType.QUEEN, Color.WHITE))
            qchess.split_move(Point(0, 0), Point(0, 1), Point(1, 1))

        def action(qchess):
            qchess.standard_move(Point(0, 2), Point(2, 0))
            qchess.engine.collapse_all()

        engine.set_board_factory(6, 3, board_factory)
        engine.set_action(action)

        engine.run_engine(500)
        engine.run_tests(self, delta=0.07)