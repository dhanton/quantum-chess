import os
import signal
import sys
import argparse
import json

from qchess.quantum_chess import QChess
from qchess.tutorial_qchess import TutorialQChess
from qchess.tutorial_progress import TutorialProgress

def signal_handler(sig, frame):
    print('')
    print('Ctrl+C was pressed. Exiting.')
    sys.exit(0)

def main():
    #handle Ctrl+C signal
    signal.signal(signal.SIGINT, signal_handler)

    epilog = 'the FILE parameter is just the name of the file, with no extension or path'

    parser = argparse.ArgumentParser(description='Quantum Chess.', epilog=epilog)

    parser.add_argument('--ascii-render', help='use the basic ascii renderer instead of PySimpleGUI',
                        action='store_true')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--game-mode', help='select a specific game mode from its configuration file in game_modes/',
                        default='micro_chess', metavar='FILE')

    group.add_argument('--tutorial', help='run a specific tutorial from its configuration file in tutorials/', metavar='FILE')

    group.add_argument('--guided-tutorials', help='run all the tutorials in order and keep track of the progress made', action='store_true')

    args = parser.parse_args()

    if args.guided_tutorials:
        tutorial_progress = TutorialProgress(args.ascii_render)
        tutorial_progress.main_loop()

    else:
        if args.tutorial:
            try:
                json_data = open(os.path.join('tutorials', args.tutorial + '.json'))
            except FileNotFoundError:
                print('Error while loading tutorial file - File not found')
                print('Please note that the ' + epilog)
                return

            qchess = TutorialQChess(json.load(json_data))

        else:
            try:
                json_data = open(os.path.join('game_modes', args.game_mode + '.json'))
            except FileNotFoundError:
                print('Error while loading game mode file - File not found')
                print('Please note that the ' + epilog)
                return

            qchess = QChess(0, 0, game_mode=json.load(json_data))

        if args.ascii_render:
            qchess.ascii_main_loop()
        else:
            qchess.create_window()
            qchess.main_loop()    

if __name__ == "__main__":
    main()
