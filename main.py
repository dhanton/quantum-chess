import os
import signal
import sys
import argparse
import json

from qchess.quantum_chess import QChess
from qchess.tutorial_qchess import TutorialQChess

def signal_handler(sig, frame):
    print('')
    print('Ctrl+C was pressed. Exiting.')
    sys.exit(0)

def main():
    #handle Ctrl+C signal
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='Quantum Chess.')

    parser.add_argument('--ascii-render', help='Use the basic ascii renderer instead of PySimpleGUI.',
                        action='store_true')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--game-mode', help='Select a game mode configuration file.',
                        default='micro_chess', metavar='FILE')

    group.add_argument('--tutorial', help='Select a tutorial configuration file.', metavar='FILE')

    args = parser.parse_args()

    if args.tutorial:
        try:
            json_data = open(os.path.join('tutorials', args.tutorial + '.json'))
        except FileNotFoundError:
            print('Error while loading tutorial file - File not found')
            return

        qchess = TutorialQChess(json.load(json_data))

    else:
        try:
            json_data = open(os.path.join('game_modes', args.game_mode + '.json'))
        except FileNotFoundError:
            print('Error while loading game mode file - File not found')
            return

        qchess = QChess(0, 0, game_mode=json.load(json_data))

    if args.ascii_render:
        qchess.ascii_main_loop()
    else:
        qchess.create_window()
        qchess.main_loop()    

if __name__ == "__main__":
    main()
