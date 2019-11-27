from qchess.quantum_chess import *

import os
import signal
import sys
import argparse
import json

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

    parser.add_argument('--game-mode', help='Select a json game mode configuration file.',
                        default='micro_chess', metavar='FILE')

    args = parser.parse_args()

    GAME_MODE_PATH = 'game_modes'

    try:
        json_data = open(os.path.join(GAME_MODE_PATH, args.game_mode + '.json'))
    except FileNotFoundError:
        print('Error while loading game mode file - File not found')
        return

    game_mode = json.load(json_data)

    qchess = QChess(0, 0, game_mode=game_mode)

    if args.ascii_render:
        qchess.ascii_main_loop()
    else:
        qchess.create_window()
        qchess.main_loop()

if __name__ == "__main__":
    main()
