from qiskit import *

import qutils
from piece import *

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.classical_board = [[NullPiece for y in range(height)] for x in range(width)]
        
        #board main quantum register
        self.qregister = QuantumRegister(width * height)
        
        #ancilla qubits used for intermediate operations
        self.aregister = QuantumRegister(4)
        
        #classical bit used as control
        self.cregister = ClassicalRegister(1)

        self.qcircuit = QuantumCircuit(self.qregister, self.aregister, self.cregister)

    def in_bounds(self, x, y):
        if x < 0 or x >= self.width:
            print("Check range Warning - x out of bounds")
            return False
        
        if y < 0 or y >= self.height:
            print("Check range Warning - y out of bounds")
            return False

        return True

    def is_occupied(self, x, y):
        if self.classical_board[x][y] != NullPiece:
            return True
        return False

    def get_qubit_index(self, x, y):
        return self.height * y + x

    def get_qubit(self, x, y):
        return self.qregister[self.get_qubit_index(x, y)]

    def add_piece(self, x, y, piece):
        if not self.in_bounds(x, y): return

        if self.is_occupied(x, y):
            print("add piece error - there is already a piece in that position")
            return

        self.classical_board[x][y] = piece

        #the value is already |0> (no piece)
        #since we want to add the piece with 100% probability, we swap to |1>
        q1 = self.qregister[self.get_qubit_index(x, y)]
        self.qcircuit.x(q1)

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

    def standard_move(self, source, target):
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

        if not piece.is_move_valid(source, target):
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
                success = qutils.perform_blocked_jump(self, source, target)

                if success:
                    self.classical_board[source.x][source.y] = NullPiece
                    self.classical_board[target.x][target.y] = piece
            else:
                success = qutils.perform_capture_jump(self, source, target)

                if success:
                    self.classical_board[source.x][source.y] = NullPiece
                    self.classical_board[target.x][target.y] = piece

        return True

    def split_move(self, source, target1, target2):
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

        if not piece.is_move_valid(source, target1) or not piece.is_move_valid(source, target2):
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
    
    def merge_move(self, source1, source2, target):
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

        if not piece1.is_move_valid(source1, target) or not piece2.is_move_valid(source2, target):
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