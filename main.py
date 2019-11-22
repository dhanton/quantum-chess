from qchess.board import *
import os

import signal
import sys

def is_game_over(board):
    black_king_count = 0
    white_king_count = 0

    msg = None

    for i in range(board.width * board.height):
        piece = board.get_piece(i)

        if piece.type == PieceType.KING:
            if piece.color == Color.WHITE:
                white_king_count += 1
            elif piece.color == Color.BLACK:
                black_king_count += 1

    if black_king_count + white_king_count == 0:
        msg = 'Draw!'

    elif black_king_count == 0:
        msg = 'White wins!'

    elif white_king_count == 0:
        msg = 'Black wins!'

    if msg:
        os.system('clear')
        board.ascii_render()
        print(msg)

        return True
    else:
        return False


def generate_micro_chess():
    board = Board(4, 5)
    board.add_piece(0, 0, Piece(PieceType.KING, Color.BLACK))
    board.add_piece(1, 0, Piece(PieceType.KNIGHT, Color.BLACK))
    board.add_piece(2, 0, Piece(PieceType.BISHOP, Color.BLACK))
    board.add_piece(3, 0, Piece(PieceType.ROOK, Color.BLACK))
    board.add_piece(3, 1, Pawn(Color.BLACK))

    board.add_piece(3, 4, Piece(PieceType.KING, Color.WHITE))
    board.add_piece(2, 4, Piece(PieceType.KNIGHT, Color.WHITE))
    board.add_piece(1, 4, Piece(PieceType.BISHOP, Color.WHITE))
    board.add_piece(0, 4, Piece(PieceType.ROOK, Color.WHITE))
    board.add_piece(3, 3, Pawn(Color.WHITE))

    return board, board.height

def test_game():
    board, height = generate_micro_chess()

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

        moved = False

        if len(command) == 4:
            #standard jump
            source = Point(ord(command[0]) - 97, height - int(command[1]))
            target = Point(ord(command[2]) - 97, height - int(command[3]))

            if board.classical_board[source.x][source.y].color != current_player:
                print('Invalid piece color')
                continue

            if board.standard_move(source, target):
                current_player = Color.WHITE if current_player == Color.BLACK else Color.BLACK
                moved = True

        elif len(command) == 7:
            if command[2] == '^':
                #split
                source = Point(ord(command[0]) - 97, height - int(command[1]))
                target1 = Point(ord(command[3]) - 97, height - int(command[4]))
                target2 = Point(ord(command[5]) - 97, height - int(command[6]))

                if board.classical_board[source.x][source.y].color != current_player:
                    print('Invalid piece color')
                    continue

                if board.split_move(source, target1, target2):
                    current_player = Color.WHITE if current_player == Color.BLACK else Color.BLACK
                    moved = True
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
                    moved = True

        if is_game_over(board):
            break

        if moved:
            moved = False
            board.perform_after_move()

def main():
    test_game()

if __name__ == "__main__":
    main()
