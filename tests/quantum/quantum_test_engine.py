from qchess.board import Board

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
            board = Board(self.width, self.height)
            self.board_factory(board)
            self.action(board)

            for bstate in self.posible_bstates:
                if bstate['state'] == board.get_simplified_matrix():
                    bstate['count'] += 1
                    break

        self.done = True

    def run_tests(self, test_case, places=None, delta=None):
        assert(self.done)

        for bstate in self.posible_bstates:
            test_case.assertAlmostEqual(bstate['count']/self.n, bstate['prob'], places=places, delta=delta)
