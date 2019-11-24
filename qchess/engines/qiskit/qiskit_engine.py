import itertools

from qiskit import *
from . import qutils

from qchess.point import Point
from qchess.piece import *
from qchess.pawn import Pawn

from qchess.engines.base_engine import BaseEngine

class QiskitEngine(BaseEngine):
    def __init__(self, qchess, width, height):
        self.qchess = qchess
        self.classical_board = qchess.board
        self.width = width
        self.height = height

        self.qflag_index = 0

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

    def on_add_piece(self, x, y, piece):
        piece.qflag = 1 << self.qflag_index
        self.qflag_index += 1

        #the value is already |0> (no piece)
        #since we want to add the piece with 100% probability, we swap to |1>
        q1 = self.get_qubit(x, y)
        self.qcircuit.x(q1)

    def get_qubit(self, x, y):
        return self.qregister[self.qchess.get_array_index(x, y)]

    def get_bit(self, x, y):
        return self.cregister[self.qchess.get_array_index(x, y)]

    def get_all_entangled_points(self, x, y):
        points = []
        qflag = self.classical_board[x][y].qflag

        if qflag != 0:
            for i in range(self.width):
                for j in range(self.height):
                    if self.classical_board[i][j].qflag & qflag != 0:
                        points.append(Point(i, j))
        
        return points

    def entangle_flags(self, qflag1, qflag2):
        #nullpiece
        if not qflag1 or not qflag2:
            return

        #already entangled
        if qflag1 & qflag2 != 0:
            return

        for i in range(self.width * self.height):
            piece = self.qchess.get_piece(i)

            if piece.qflag & qflag1 != 0:
                piece.qflag |= qflag2

            elif piece.qflag & qflag2 != 0:
                piece.qflag |= qflag1

    def entangle_path_flags(self, qflag, source, target):
        all_qflags = 0

        pieces = self.qchess.get_path_pieces(source, target)

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
            piece = self.qchess.get_piece(i)

            if (
                # not self.is_piece_collapsed(i) and
                piece != NullPiece and (collapse_all or piece.qflag & qflag != 0)
            ):
                #measure the ith qubit to the ith bit
                self.qcircuit.measure(self.qregister[i], self.cregister[i])
                collapsed_indices.append(i)
        
        if not collapsed_indices:
            return

        job = execute(self.qcircuit, backend=qutils.backend, shots=1)
        result = job.result()

        bitstring = list(result.get_counts().keys())[0].split(' ')[1]

        for i, char in enumerate(bitstring[::-1]):
            if char == '0' and i in collapsed_indices:
                pos = self.qchess.get_board_point(i)
                self.classical_board[pos.x][pos.y] = NullPiece

                #set to |0> in circuit
                self.qcircuit.reset(self.qregister[i])

            if char == '1' and i in collapsed_indices:
                #set to |1> in circuit
                self.qcircuit.reset(self.qregister[i])
                self.qcircuit.x(self.qregister[i])

    def collapse_path(self, source, target, collapse_target=False, collapse_source=False):
        qflag = 0

        for piece in self.qchess.get_path_pieces(source, target):
            qflag |= piece.qflag

        source_piece = self.classical_board[source.x][source.y]
        if source_piece != NullPiece and collapse_source:
            qflag |= source_piece.qflag

        target_piece = self.classical_board[target.x][target.y]
        if target_piece != NullPiece and collapse_source:
            qflag |= target_piece.qflag

        self.collapse_by_flag(qflag)

        #return true if path is clear after collapse
        return not bool(self.qchess.get_path_pieces(source, target))

    def collapse_point(self, x, y):
        self.collapse_by_flag(self.classical_board[x][y].qflag)

    def collapse_all(self):
        self.collapse_by_flag(None, collapse_all=True)

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
        path = self.qchess.get_path_points(source, target)

        for i in range(self.width * self.height):
            point = self.qchess.get_board_point(i)

            if self.classical_board[point.x][point.y].qflag & target_piece.qflag != 0:
                entangled_points.append(point)

        #if a piece is blocking the path independently of the entanglement
        #of target, then DO is always violated
        for i, point in enumerate(path):
            if not point in entangled_points and self.qchess.get_piece(i) != NullPiece:
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

    def standard_move(self, source, target, force=False):
        piece = self.classical_board[source.x][source.y]

        if not force and piece.type == PieceType.PAWN:
            return self._standard_pawn_move(source, target)

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
                                path_clear = self.collapse_path(source, target, collapse_source=True)

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

    def _standard_pawn_move(self, source, target):
        pawn = self.classical_board[source.x][source.y]
        target_piece = self.classical_board[target.x][target.y]

        move_type, ep_point = pawn.is_move_valid(source, target, qchess=self.qchess)
        
        #this is checked in QChess class
        assert(move_type != Pawn.MoveType.INVALID)

        new_source_piece = pawn
        new_target_piece = target_piece

        if (
            move_type == Pawn.MoveType.SINGLE_STEP or
            move_type == Pawn.MoveType.DOUBLE_STEP
        ):
            self.collapse_by_flag(target_piece.qflag)

            if (
                self.classical_board[source.x][source.y] != NullPiece and
                self.classical_board[target.x][target.y] == NullPiece
            ):
                if move_type == Pawn.MoveType.SINGLE_STEP:
                    qutils.perform_standard_jump(self, source, target)

                    new_source_piece = NullPiece
                else:
                    if not self.entangle_path_flags(pawn.qflag, source, target):
                        new_source_piece = NullPiece

                    qutils.perform_standard_slide(self, source, target)

                new_target_piece = pawn

        elif move_type == Pawn.MoveType.CAPTURE:
            #pawn is the only piece that needs to collapse target when capturing
            #because it can't move diagonally unless capturing
            self.collapse_by_flag(pawn.qflag | target_piece.qflag)

            if (
                self.classical_board[source.x][source.y] != NullPiece and
                self.classical_board[target.x][target.y] != NullPiece
            ):
                qutils.perform_capture_jump(self, source, target)

                new_source_piece = NullPiece
                new_target_piece = pawn

        elif move_type == Pawn.MoveType.EN_PASSANT:
            if target_piece == NullPiece:
                qutils.perform_standard_en_passant(self, source, target, ep_point)

                new_source_piece = NullPiece
                new_target_piece = pawn
                self.classical_board[ep_point.x][ep_point.y] = NullPiece

            elif target_piece.color == pawn.color:
                self.collapse_by_flag(target_piece.qflag)

                if self.classical_board[target.x][target.y] == NullPiece:
                    qutils.perform_standard_en_passant(self, source, target, ep_point)
                    
                    new_source_piece = NullPiece
                    new_target_piece = pawn
                    self.classical_board[ep_point.x][ep_point.y] = NullPiece
            else:
                self.collapse_by_flag(pawn.qflag)

                if self.classical_board[source.x][source.y] != NullPiece:
                    qutils.perform_capture_en_passant(self, source, target, ep_point)

                    new_source_piece = NullPiece
                    new_target_piece = pawn
                    self.classical_board[ep_point.x][ep_point.y] = NullPiece

        self.classical_board[source.x][source.y] = new_source_piece
        self.classical_board[target.x][target.y] = new_target_piece

    def split_move(self, source, target1, target2):
        piece = self.classical_board[source.x][source.y]
        target_piece1 = self.classical_board[target1.x][target1.y]
        target_piece2 = self.classical_board[target2.x][target2.y]

        new_source_piece = NullPiece

        if piece.is_move_slide():
            qutils.perform_split_slide(self, source, target1, target2)

            path1_blocked = self.entangle_path_flags(piece.qflag, source, target1)
            path2_blocked = self.entangle_path_flags(piece.qflag, source, target2)
            
            #set the source piece to null if any of the paths is not blocked,
            #since the piece will always slide through that one if the other is blocked
            if path1_blocked and path2_blocked:
                new_source_piece = piece
        else:
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
            self.classical_board[source.x][source.y] = new_source_piece
    
    def merge_move(self, source1, source2, target):
        piece1 = self.classical_board[source1.x][source1.y]
        piece2 = self.classical_board[source2.x][source2.y]
        target_piece = self.classical_board[target.x][target.y]

        new_source1_piece = NullPiece
        new_source2_piece = NullPiece

        if piece1.is_move_slide:
            qutils.perform_merge_slide(self, source1, source2, target)

            #set source piece to null only if the path for that piece is not blocked,
            #since if it's blocked then the piece might not be able to slide through
            if self.entangle_path_flags(piece1.qflag, source1, target):
                new_source1_piece = piece1

            if self.entangle_path_flags(piece2.qflag, source2, target):
                new_source2_piece = piece2

        else:
            qutils.perform_merge_jump(self, source1, source2, target)

        #we should only entangle flags between the qubits to which we apply iswap_sqrt
        #TODO: find best way to do this        
        self.entangle_flags(piece1.qflag, piece2.qflag)
        self.entangle_flags(piece1.qflag, target_piece.qflag)

        self.classical_board[target.x][target.y] = piece1

        if target_piece == NullPiece:
            self.classical_board[source1.x][source1.y] = new_source1_piece
            self.classical_board[source2.x][source2.y] = new_source2_piece