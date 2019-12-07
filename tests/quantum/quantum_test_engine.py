#import shots and delta default values
from . import *

from qchess.quantum_chess import QChess

class QuantumTestEngine():
    def __init__(self):
        self.posible_bstates = []
        self.done = False

    def add_board_state(self, state, prob):
        self.posible_bstates.append({'state': state, 'prob': prob, 'count': 0})

    def set_action(self, action):
        self.action = action

    def set_board_factory(self, width, height, func):
        self.width = width
        self.height = height
        self.board_factory = func

    def run_engine(self, n):
        assert(self.action)
        assert(self.posible_bstates)
        assert(self.width > 0 and self.height > 0)
        assert(self.board_factory)

        self.n = n

        for i in range(n):
            qchess = QChess(self.width, self.height)
            self.board_factory(qchess)
            self.action(qchess)

            for bstate in self.posible_bstates:
                if bstate['state'] == qchess.get_simplified_matrix():
                    bstate['count'] += 1
                    break

        self.done = True

    def run_tests(self, test_case, places=None, delta=None):
        assert(self.done)

        if display_probabilities:
            print()

            #we display the probabilites in another loop to be able
            #to display all even if assert fails
            for bstate in self.posible_bstates:
                print('Obtained: {} Expected: {}'.format(round(bstate['count']/self.n, 2), bstate['prob']))

        for bstate in self.posible_bstates:
            test_case.assertAlmostEqual(bstate['count']/self.n, bstate['prob'], places=places, delta=delta)
