import itertools

from qiskit import *

from . import qutils
from .point import Point
from .piece import *

class Board:
    def __init__(self, width, height):
        self.qflag_index = 0
        self.width = width
        self.height = height

        self.classical_board = [[NullPiece for y in range(height)] for x in range(width)]
        
        #board main quantum register
        self.qregister = QuantumRegister(width * height)
        
        #ancilla qubits used for some intermediate operations
        self.aregister = QuantumRegister(3)

        #ancilla qubits used by the mct function in qutils
        self.mct_register = QuantumRegister(6)
        
        #classical bits to collapse each square individually
        self.cregister = ClassicalRegister(width * height)

        #classical bit for other operations
        self.cbit_misc = ClassicalRegister(1)

        self.qcircuit = QuantumCircuit(self.qregister, self.aregister, self.mct_register, self.cregister, self.cbit_misc)

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
        return self.width * y + x

    def get_board_point(self, index):
        return Point(index%self.width, int(index/self.width))

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

        piece.qflag = 1 << self.qflag_index
        self.qflag_index += 1

        self.classical_board[x][y] = piece

        #the value is already |0> (no piece)
        #since we want to add the piece with 100% probability, we swap to |1>
        q1 = self.get_qubit(x, y)
        self.qcircuit.x(q1)

    #deprecated
    def _is_piece_collapsed(self, i):
        piece = self.get_piece(i)

        if piece == NullPiece:
            return False

        for j in range(self.width * self.height):
            if i == j: continue

            p = self.get_piece(j)
            
            if  p.qflag & piece.qflag != 0:
                return False

        return True

    def get_path_points(self, source, target):
        #not including source or target
        path = []
        
        if not self.in_bounds(source.x, source.y): return path 
        if not self.in_bounds(target.x, target.y): return path
        if source == target: return path

        vec = target - source
        if vec.x != 0 and vec.y != 0 and vec.x != vec.y: return path

        x_iter = y_iter = 0

        if vec.x != 0:
            x_iter = vec.x/abs(vec.x)
        if vec.y != 0:
            y_iter = vec.y/abs(vec.y)

        for i in range(1, max(abs(vec.x), abs(vec.y))):
            path.append(source + Point(x_iter * i, y_iter * i))

        return path

    def get_path_pieces(self, source, target):
        pieces = []

        for point in self.get_path_points(source, target):
            if self.classical_board[point.x][point.y] != NullPiece:
                pieces.append(self.classical_board[point.x][point.y])
        
        return pieces

    def entangle_flags(self, qflag1, qflag2):
        #nullpiece
        if not qflag1 or not qflag2:
            return

        #already entangled
        if qflag1 & qflag2 != 0:
            return

        for i in range(self.width * self.height):
            piece = self.get_piece(i)

            if piece.qflag & qflag1 != 0:
                piece.qflag |= qflag2

            elif piece.qflag & qflag2 != 0:
                piece.qflag |= qflag1

    def entangle_path_flags(self, qflag, source, target):
        all_qflags = 0

        pieces = self.get_path_pieces(source, target)

        for piece in pieces:
            all_qflags |= piece.qflag
        
        self.entangle_flags(all_qflags, qflag)

        return bool(pieces)

    def collapse_by_flag(self, qflag, collapse_all=False):
        #nullpiece
        if not qflag and not collapse_all:
            return

        collapsed_indices = []

        for i in range(self.width * self.height):
            piece = self.get_piece(i)

            if (
                # not self.is_piece_collapsed(i) and
                piece != NullPiece and (collapse_all or piece.qflag & qflag != 0)
            ):
                #measure the ith qubit to the ith bit
                self.qcircuit.measure(self.qregister[i], self.cregister[i])
                collapsed_indices.append(i)
        
        if not collapsed_indices:
            return

        result = execute(self.qcircuit, backend=qutils.backend, shots=1).result()
        bitstring = list(result.get_counts().keys())[0].split(' ')[1]

        for i, char in enumerate(bitstring[::-1]):
            if char == '0' and i in collapsed_indices:
                pos = self.get_board_point(i)
                self.classical_board[pos.x][pos.y] = NullPiece

                #set to |0> in circuit
                self.qcircuit.reset(self.qregister[i])

            if char == '1' and i in collapsed_indices:
                #set to |1> in circuit
                self.qcircuit.reset(self.qregister[i])
                self.qcircuit.x(self.qregister[i])

    def collapse_path(self, source, target, collapse_target=False, collapse_source=False):
        qflag = 0

        for piece in self.get_path_pieces(source, target):
            qflag |= piece.qflag

        source_piece = self.classical_board[source.x][source.y]
        if source_piece != NullPiece and collapse_source:
            qflag |= source_piece.qflag

        target_piece = self.classical_board[target.x][target.y]
        if target_piece != NullPiece and collapse_source:
            qflag |= target_piece.qflag

        self.collapse_by_flag(qflag)

        #return true if path is clear after collapse
        return not bool(self.get_path_pieces(source, target))

    """
        This function will atempt (with only access to classical info)
        to tell if a slide move could violate the double occupancy
        rule.

        This function is called after qutils.perform_slide_capture
        only if true was returned. So the path is clear in at least
        one of the superpositions, or the path is blocked but target
        is empty.
    """
    def does_slide_violate_double_occupancy(self, source, target):
        target_piece = self.classical_board[target.x][target.y]

        if target_piece == NullPiece: 
            #target is always empty
            return False

        entangled_points = []
        path = self.get_path_points(source, target)

        for i in range(self.width * self.height):
            point = self.get_board_point(i)

            if self.classical_board[point.x][point.y].qflag & target_piece.qflag != 0:
                entangled_points.append(point)

        #if a piece is blocking the path independently of the entanglement
        #of target, then DO is always violated
        for i, point in enumerate(path):
            if not point in entangled_points and self.get_piece(i) != NullPiece:
                return True

        #the number of pieces is the number of 1s in the target qflag
        number_of_pieces = list(bin(target_piece.qflag)).count('1')

        assert(len(entangled_points) >= number_of_pieces)

        #contains 1 for each piece and the rest are zeroes (empty squares)
        permutations = [1] * number_of_pieces + [0] * (len(entangled_points) - number_of_pieces)

        #unique permutations of number of pieces in all points
        permutations = set(list(itertools.permutations(permutations)))

        for perm in permutations:
            blocked = False
            target_empty = True

            #entangled_points and all permutations have the same length
            #so they correspond to the same point for the same index
            for i, point in enumerate(entangled_points):
                if point in path and perm[i] == 1:
                    blocked = True

                if point == target and perm[i] == 1:
                    target_empty = False

            if blocked and not target_empty:
                return True

        return False

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

        if target_piece == NullPiece or target_piece == piece:
            if piece.is_move_slide():
                if (
                    self.entangle_path_flags(piece.qflag, source, target) and 
                    target_piece == NullPiece
                ):
                    #if something may be blocking then the piece might stay in place
                    #so we don't want to remove it clasically
                    target_piece = piece
                
                qutils.perform_standard_slide(self, source, target)
            else:
                qutils.perform_standard_jump(self, source, target)

            self.classical_board[source.x][source.y] = target_piece
            self.classical_board[target.x][target.y] = piece
        else:
            if target_piece.color == piece.color:
                self.collapse_by_flag(target_piece.qflag)

                if (
                    self.classical_board[source.x][source.y] != NullPiece and
                    self.classical_board[target.x][target.y] == NullPiece
                ):
                    new_source_piece = NullPiece

                    if piece.is_move_slide():
                        if self.entangle_path_flags(piece.qflag, source, target):
                            #if something may be blocking then the piece might stay in place
                            #so we don't want to remove it clasically
                            new_source_piece = piece
                        
                        qutils.perform_standard_slide(self, source, target)
                    else:
                        qutils.perform_standard_jump(self, source, target)

                    self.classical_board[source.x][source.y] = new_source_piece
                    self.classical_board[target.x][target.y] = piece
            else:
                self.collapse_by_flag(piece.qflag)

                if self.classical_board[source.x][source.y] != NullPiece:
                    if piece.is_move_slide():
                        """
                            Afer qutils.perform_capture_slide the path is collapsed
                            already unless does_slide_violate_double_occupancy returns 0,
                            in which case entanglement occurs.
                            We call collapse_path to update the classical board.
                        """
                        if qutils.perform_capture_slide(self, source, target):
                            if self.does_slide_violate_double_occupancy(source, target):
                                path_clear =  self.collapse_path(source, target, collapse_source=True)

                                if path_clear and self.classical_board[source.x][source.y] == NullPiece:
                                    self.classical_board[target.x][target.y] = piece
                            else:
                                if not self.entangle_path_flags(piece.qflag, source, target):
                                    self.classical_board[source.x][source.y] = NullPiece
                                    
                                self.classical_board[target.x][target.y] = piece
                        else:
                            path_clear = self.collapse_path(source, target, collapse_source=True)

                            if path_clear and self.classical_board[source.x][source.y] == NullPiece:
                                self.classical_board[target.x][target.y] = piece
                    else:
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

        #we should only entangle flags between the qubits to which we apply iswap_sqrt
        #TODO: find best way to do this
        self.entangle_flags(piece.qflag, target_piece1.qflag)
        self.entangle_flags(piece.qflag, target_piece2.qflag)

        if target_piece1 == NullPiece:
            self.classical_board[target1.x][target1.y] = piece

        if target_piece2 == NullPiece:
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

        #we should only entangle flags between the qubits to which we apply iswap_sqrt
        #TODO: find best way to do this        
        self.entangle_flags(piece1.qflag, piece2.qflag)
        self.entangle_flags(piece1.qflag, target_piece.qflag)

        self.classical_board[target.x][target.y] = piece1

        if target_piece == NullPiece:
            self.classical_board[source1.x][source1.y] = NullPiece
            self.classical_board[source2.x][source2.y] = NullPiece

        return True
