from qiskit import *

from . import qutils
from .piece import *

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Board:
    def __init__(self, width, height):
        self.qhash_index = 0
        self.width = width
        self.height = height

        self.classical_board = [[NullPiece for y in range(height)] for x in range(width)]
        
        #board main quantum register
        self.qregister = QuantumRegister(width * height)
        
        #ancilla qubits used for intermediate operations
        self.aregister = QuantumRegister(4)
        
        #classical bit to collapse each square individually
        self.cregister = ClassicalRegister(width * height)

        self.qcircuit = QuantumCircuit(self.qregister, self.aregister, self.cregister)

    def in_bounds(self, x, y):
        if x < 0 or x >= self.width:
            return False
        
        if y < 0 or y >= self.height:
            return False

        return True

    def is_occupied(self, x, y):
        if self.classical_board[x][y] != NullPiece:
            return True
        return False

    def get_array_index(self, x, y):
        return self.height * y + x

    def get_board_point(self, index):
        return Point(index%self.width, int(index/self.height))

    def get_qubit(self, x, y):
        return self.qregister[self.get_array_index(x, y)]

    def get_bit(self, x, y):
        return self.cregister[self.get_array_index(x, y)]

    def get_piece(self, index):
        pos = self.get_board_point(index)
        return self.classical_board[pos.x][pos.y]

    def add_piece(self, x, y, piece):
        if not self.in_bounds(x, y): return

        if self.is_occupied(x, y):
            print("add piece error - there is already a piece in that position")
            return

        piece.qhash = 1 << self.qhash_index
        self.qhash_index += 1

        self.classical_board[x][y] = piece

        #the value is already |0> (no piece)
        #since we want to add the piece with 100% probability, we swap to |1>
        q1 = self.get_qubit(x, y)
        self.qcircuit.x(q1)

    def collapse_by_hash(self, qhash):
        collapsed_indices = []

        for i in range(self.width * self.height):
            piece = self.get_piece(i)

            if piece != NullPiece and piece.qhash & qhash != 0:
                #measure the ith qubit to the ith bit
                self.qcircuit.measure(i, i)
                collapsed_indices.append(i)
        
        result = execute(self.qcircuit, backend=qutils.backend, shots=1).result()
        bitstring = list(result.get_counts().keys())[0]

        for i, char in enumerate(bitstring[::-1]):
            if char == '0' and i in collapsed_indices:
                pos = self.get_board_point(i)
                self.classical_board[pos.x][pos.y] = NullPiece


    def ascii_render(self):
        s = ""

        for j in range(self.height):
            for i in range(self.width):
                piece = self.classical_board[i][j]
                if piece:
                    s += piece.as_notation() + ' '
                else:
                    s += '0 '
            s += '\n'

        print(s)

    def get_simplified_matrix(self):
        m = []

        for j in range(self.height):
            row = []
            for i in range(self.width):
                row.append(self.classical_board[i][j].as_notation())
            m.append(row)

        return m

    def standard_move(self, source, target, force=False):
        if not self.in_bounds(source.x, source.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(target.x, target.y):
            print('Invalid move - Target square not in bounds')
            return False
        
        if not self.is_occupied(source.x, source.y):
            print('Invalid move - Source square is empty')
            return False

        piece = self.classical_board[source.x][source.y]    

        if not force and not piece.is_move_valid(source, target):
            print('Invalid move - Incorrect move for piece type ' + piece.type.name.lower())
            return False

        target_piece = self.classical_board[target.x][target.y]

        """
        TODO: Handle slides and pawns properly
              For slides:
                    * If anything is blocking the path, then dont remove source clasically
                    * If nothing is blocking the path, remove source clasically
        """

        if target_piece == NullPiece or target_piece == piece:
            qutils.perform_standard_jump(self, source, target)

            self.classical_board[source.x][source.y] = target_piece
            self.classical_board[target.x][target.y] = piece
        else:
            if target_piece.color == piece.color:
                self.collapse_by_hash(target_piece.qhash)

                if self.classical_board[target.x][target.y] == NullPiece:
                    qutils.perform_standard_jump(self, source, target)

                    self.classical_board[source.x][source.y] = NullPiece
                    self.classical_board[target.x][target.y] = piece
            else:
                self.collapse_by_hash(piece.qhash)

                if self.classical_board[source.x][source.y] != NullPiece:
                    qutils.perform_capture_jump(self, source, target)

                    self.classical_board[source.x][source.y] = NullPiece
                    self.classical_board[target.x][target.y] = piece

        return True

    def split_move(self, source, target1, target2, force=False):
        if not self.in_bounds(source.x, source.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(target1.x, target1.y) or not self.in_bounds(target2.x, target2.y):
            print('Invalid move - Target square not in bounds')
            return False
        
        if not self.is_occupied(source.x, source.y):
            print('Invalid move - Source square is empty')
            return False

        if target1 == target2:
            print("Invalid move - Both split targets are the same square")
            return False
        
        piece = self.classical_board[source.x][source.y]

        if not force and (not piece.is_move_valid(source, target1) or not piece.is_move_valid(source, target2)):
            print('Invalid move - Incorrect move for piece type ' + piece.type.name.lower())
            return False

        target_piece1 = self.classical_board[target1.x][target1.y]
        target_piece2 = self.classical_board[target2.x][target2.y]

        if target_piece1 != NullPiece and target_piece1.type != piece.type:
            print("Invalid move - Target square is not empty")
            return False

        if target_piece2 != NullPiece and target_piece2.type != piece.type:
            print("Invalid move - Target square is not empty")
            return False

        qutils.perform_split_jump(self, source, target1, target2)

        self.classical_board[target1.x][target1.y] = piece
        self.classical_board[target2.x][target2.y] = piece

        if target_piece1 == NullPiece and target_piece2 == NullPiece:
            self.classical_board[source.x][source.y] = NullPiece

        return True
    
    def merge_move(self, source1, source2, target, force=False):
        if not self.in_bounds(source1.x, source1.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(source2.x, source2.y):
            print('Invalid move - Source square not in bounds')
            return False

        if not self.in_bounds(target.x, target.y):
            print('Invalid move - Target square not in bounds')
            return False

        if source1 == source2:
            print('Invalid move - Both merge sources are the same squares')
            return False
        
        piece1 = self.classical_board[source1.x][source1.y]
        piece2 = self.classical_board[source2.x][source2.y]

        if piece1 != piece2:
            print('Invalid move - Different type of merge source pieces')
            return False

        if not force and (not piece1.is_move_valid(source1, target) or not piece2.is_move_valid(source2, target)):
            print('Invalid move - Incorrect move for piece type ' + piece1.type.lower())
            return False

        target_piece = self.classical_board[target.x][target.y]

        if target_piece != NullPiece and target_piece.type != piece1.type:
            print('Invalid move - Target square is not empty')
            return False

        qutils.perform_merge_jump(self, source1, source2, target)

        self.classical_board[target.x][target.y] = piece1

        if target_piece == NullPiece:
            self.classical_board[source1.x][source1.y] = NullPiece
            self.classical_board[source2.x][source2.y] = NullPiece

        return True