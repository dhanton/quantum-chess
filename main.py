from board import *
import os

import signal
import sys

def test_game():
    board = Board(4, 4)
    board.add_piece(0, 0, Piece(PieceType.KING, Color.WHITE))
    board.add_piece(3, 3, Piece(PieceType.KING, Color.BLACK))

    current_player = Color.WHITE

    def signal_handler(sig, frame):
        print("Circuit:")
        print(board.qcircuit.draw())
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    while(True):
        os.system('clear')
        board.ascii_render()

        command = input('')

        if len(command) == 4:
            #standard jump
            source = Point(ord(command[0]) - 97, 4 - int(command[1]))
            target = Point(ord(command[2]) - 97, 4 - int(command[3]))

            if board.classical_board[source.x][source.y].color != current_player:
                print('Invalid piece color')
                continue

            if board.standard_move(source, target):
                current_player = Color.WHITE if current_player == Color.BLACK else Color.BLACK

        elif len(command) == 7:
            if command[2] == '^':
                #split
                source = Point(ord(command[0]) - 97, 4 - int(command[1]))
                target1 = Point(ord(command[3]) - 97, 4 - int(command[4]))
                target2 = Point(ord(command[5]) - 97, 4 - int(command[6]))

                if board.classical_board[source.x][source.y].color != current_player:
                    print('Invalid piece color')
                    continue

                if board.split_move(source, target1, target2):
                    current_player = Color.WHITE if current_player == Color.BLACK else Color.BLACK
            else:
                #merge
                source1 = Point(ord(command[0]) - 97, 4 - int(command[1]))
                source2 = Point(ord(command[2]) - 97, 4 - int(command[3]))
                target = Point(ord(command[5]) - 97, 4 - int(command[6]))
                
                if board.classical_board[source1.x][source1.y].color != current_player or \
                    board.classical_board[source2.x][source2.y].color != current_player:
                    print('Invalid piece color')
                    continue

                if board.merge_move(source1, source2, target):
                    current_player = Color.WHITE if current_player == Color.BLACK else Color.BLACK

def main():
    test_game()

    """
    Test multiple combinations of different moves
        In particular how multiple execute() affect the circuit
        Can it still be used afterwards?
        Add these tests in tests.py
    """


if __name__ == "__main__":
    main()