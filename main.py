from qchess.quantum_chess import *

import os
import signal
import sys

#deprecated
def generate_micro_chess():
    qchess = QChess(4, 5)
    qchess.add_piece(0, 0, Piece(PieceType.KING, Color.BLACK))
    qchess.add_piece(1, 0, Piece(PieceType.KNIGHT, Color.BLACK))
    qchess.add_piece(2, 0, Piece(PieceType.BISHOP, Color.BLACK))
    qchess.add_piece(3, 0, Piece(PieceType.ROOK, Color.BLACK))
    qchess.add_piece(3, 1, Pawn(Color.BLACK))

    qchess.add_piece(3, 4, Piece(PieceType.KING, Color.WHITE))
    qchess.add_piece(2, 4, Piece(PieceType.KNIGHT, Color.WHITE))
    qchess.add_piece(1, 4, Piece(PieceType.BISHOP, Color.WHITE))
    qchess.add_piece(0, 4, Piece(PieceType.ROOK, Color.WHITE))
    qchess.add_piece(3, 3, Pawn(Color.WHITE))

    return qchess, qchess.height

#deprecated
def test_game():
    qchess, height = generate_micro_chess()

    current_player = Color.WHITE

    def signal_handler(sig, frame):
        if type(qchess.engine) == QiskitEngine:
            print("Circuit:")
            print(qchess.engine.qcircuit.draw())
            sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        os.system('clear')
        qchess.ascii_render()

        command = input('')

        moved = False

        if len(command) == 4:
            #standard jump
            source = Point(ord(command[0]) - 97, height - int(command[1]))
            target = Point(ord(command[2]) - 97, height - int(command[3]))

            if qchess.board[source.x][source.y].color != current_player:
                print('Invalid piece color')
                continue

            if qchess.standard_move(source, target):
                current_player = Color.WHITE if current_player == Color.BLACK else Color.BLACK
                moved = True

        elif len(command) == 7:
            if command[2] == '^':
                #split
                source = Point(ord(command[0]) - 97, height - int(command[1]))
                target1 = Point(ord(command[3]) - 97, height - int(command[4]))
                target2 = Point(ord(command[5]) - 97, height - int(command[6]))

                if qchess.board[source.x][source.y].color != current_player:
                    print('Invalid piece color')
                    continue

                if qchess.split_move(source, target1, target2):
                    current_player = Color.opposite(current_player)
                    moved = True
            else:
                #merge
                source1 = Point(ord(command[0]) - 97, 4 - int(command[1]))
                source2 = Point(ord(command[2]) - 97, 4 - int(command[3]))
                target = Point(ord(command[5]) - 97, 4 - int(command[6]))
                
                if qchess.board[source1.x][source1.y].color != current_player or \
                    qchess.board[source2.x][source2.y].color != current_player:
                    print('Invalid piece color')
                    continue

                if qchess.merge_move(source1, source2, target):
                    current_player = Color.opposite(current_player)
                    moved = True

        if qchess.is_game_over():
            qchess.ascii_render()
            break

        if moved:
            moved = False
            qchess.perform_after_move()

def main():
    qchess = QChess(3, 3)

    qchess.create_window()
    qchess.main_loop()

if __name__ == "__main__":
    main()
