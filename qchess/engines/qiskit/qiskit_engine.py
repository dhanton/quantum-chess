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

        NullPiece.qflag = 0
        self.qflag_index = 0

        self.generate_circuit()

    def generate_circuit(self):
        #board main quantum register
        self.qregister = QuantumRegister(self.width * self.height)
        
        #ancilla qubits used for some intermediate operations
        self.aregister = QuantumRegister(3)

        #ancilla qubits used by the mct function in qutils
        self.mct_register = QuantumRegister(6)
        
        #classical bits to collapse each square individually
        self.cregister = ClassicalRegister(self.width * self.height)

        #classical bit for other operations
        self.cbit_misc = ClassicalRegister(1)

        self.qcircuit = QuantumCircuit(self.qregister, self.aregister, self.mct_register, self.cregister, self.cbit_misc)

        #populate the qubits if pieces already exist
        for i in range(self.width * self.height):
            if self.qchess.get_piece(i) != NullPiece:
                self.qcircuit.x(self.qregister[i])

    def on_add_piece(self, x, y, piece):
        piece.qflag = 1 << self.qflag_index
        self.qflag_index += 1

        #the value is already |0> (no piece)
        #since we want to add the piece with 100% probability, we swap to |1>
        q1 = self.get_qubit(x, y)
        self.qcircuit.x(q1)

    def on_pawn_promotion(self, promoted_pawn, pawn):
        promoted_pawn.qflag = pawn.qflag

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
                not piece.collapsed and
                piece != NullPiece and (collapse_all or piece.qflag & qflag != 0)
            ):
                #measure the ith qubit to the ith bit
                self.qcircuit.measure(self.qregister[i], self.cregister[i])
                collapsed_indices.append(i)
        
        if collapsed_indices:
            job = execute(self.qcircuit, backend=qutils.backend, shots=1)
            result = job.result()

            bitstring = list(result.get_counts().keys())[0].split(' ')[1]

            if collapse_all:
                self.qflag_index = 0

            for i, char in enumerate(bitstring[::-1]):
                pos = self.qchess.get_board_point(i)

                if char == '0' and i in collapsed_indices:
                    self.classical_board[pos.x][pos.y] = NullPiece

                    #set to |0> in circuit
                    self.qcircuit.reset(self.qregister[i])

                if char == '1' and i in collapsed_indices:
                    #set to |1> in circuit
                    self.qcircuit.reset(self.qregister[i])
                    self.qcircuit.x(self.qregister[i])

                    piece = self.qchess.get_piece(i)
                    assert(piece != NullPiece)
                    piece.collapsed = True

                    #since we can't be 100% sure of the original qflag of a piece
                    #we assign them at random from the qflag used to collapse
                    #(note: binary qflag has as many '1's as the number of collapsed pieces)

                    if not collapse_all:
                        #find the position of the first '1' in binary qflag
                        binary_qflag = bin(qflag)[2:]
                        index = len(binary_qflag) - binary_qflag.find('1') - 1

                        #there should always be enough '1's for every collapsed piece
                        assert(index < len(bin(qflag)))

                        #generate a new qflag with all '0's except a '1' in that position
                        new_qflag = 1 << index

                        #remove the '1' in that position from binary qflag
                        qflag ^= new_qflag
                    else:
                        new_qflag = 1 << self.qflag_index
                        self.qflag_index += 1

                    #assign new original qflag
                    piece.qflag = new_qflag 
                    
        all_collapsed = collapse_all

        if not all_collapsed:
            all_collapsed = True

            for i in range(self.width * self.height):
                if not self.qchess.get_piece(i).collapsed:
                    all_collapsed = False
                    break

        #the circuit is reset when all pieces are collapsed, even if
        #no new pieces were collapsed in this call
        #when all the qubits are |0> or |1>, it's cheaper to just reset
        #the circuit than to keep track of all the qubits operations
        if all_collapsed:
            self.generate_circuit()

    def set_piece_uncollapsed(self, point):
        if self.classical_board[point.x][point.y] != NullPiece:
            self.classical_board[point.x][point.y].collapsed = False

    def collapse_path(self, source, target, collapse_target=False, collapse_source=False):
        qflag = 0

        for piece in self.qchess.get_path_pieces(source, target):
            qflag |= piece.qflag

        source_piece = self.classical_board[source.x][source.y]
        if source_piece != NullPiece and collapse_source:
            #force the piece to get collapsed
            source_piece.collapsed = False

            qflag |= source_piece.qflag

        target_piece = self.classical_board[target.x][target.y]
        if target_piece != NullPiece and collapse_source:
            #force the piece to get collapsed
            target_piece.collapsed = False

            qflag |= target_piece.qflag

        self.collapse_by_flag(qflag)

        #return true if path is clear after collapse
        return not bool(self.qchess.get_path_pieces(source, target))

    def collapse_point(self, x, y):
        self.collapse_by_flag(self.classical_board[x][y].qflag)

    def collapse_all(self):
        self.collapse_by_flag(None, collapse_all=True)

    """
        The idea of this function is to calculate all posible permutations
        of the pieces entangled with target to see if, in any of the combinations,
        target is not empty and the path is blocked at the same time. This
        would violate double occupancy so a measurement has to be performed.
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
        #of target, then DO is violated
        for point in path:
            if self.classical_board[point.x][point.y] != NullPiece and not point in entangled_points:
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
                if self.entangle_path_flags(piece.qflag, source, target):
                    piece.collapsed = False

                    #if something may be blocking then the piece might stay in place
                    #so we don't want to remove it clasically
                    if target_piece == NullPiece:
                        target_piece = piece
                
                qutils.perform_standard_slide(self, source, target)
            else:
                qutils.perform_standard_jump(self, source, target)

            self.classical_board[source.x][source.y] = target_piece.copy()
            self.classical_board[target.x][target.y] = piece.copy()
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
                            piece.collapsed = False
                            new_source_piece = piece
                        
                        qutils.perform_standard_slide(self, source, target)
                    else:
                        qutils.perform_standard_jump(self, source, target)

                    self.classical_board[source.x][source.y] = new_source_piece.copy()
                    self.classical_board[target.x][target.y] = piece.copy()
            else:
                self.collapse_by_flag(piece.qflag)

                if self.classical_board[source.x][source.y] != NullPiece:
                    path_empty = self.qchess.is_path_empty(source, target)

                    #if the path is empty the move is just a jump
                    if piece.is_move_slide() and not path_empty:
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
                                    self.classical_board[target.x][target.y] = piece.copy()
                            else:
                                if not self.entangle_path_flags(piece.qflag, source, target):
                                    self.classical_board[source.x][source.y] = NullPiece
                                else:
                                    piece.collapsed = False
                                    
                                self.classical_board[target.x][target.y] = piece.copy()
                        else:
                            path_clear = self.collapse_path(source, target, collapse_source=True)

                            if path_clear and self.classical_board[source.x][source.y] == NullPiece:
                                self.classical_board[target.x][target.y] = piece.copy()
                    else:
                        qutils.perform_capture_jump(self, source, target)

                        self.classical_board[source.x][source.y] = NullPiece
                        self.classical_board[target.x][target.y] = piece.copy()

    def _standard_pawn_move(self, source, target):
        pawn = self.classical_board[source.x][source.y]
        target_piece = self.classical_board[target.x][target.y]

        move_type, ep_point = pawn.is_move_valid(source, target, qchess=self.qchess)
        
        #this is checked in QChess class
        assert(move_type != Pawn.MoveType.INVALID)

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

                    self.classical_board[source.x][source.y] = NullPiece
                else:
                    if not self.entangle_path_flags(pawn.qflag, source, target):
                        self.classical_board[source.x][source.y] = NullPiece
                    else:
                        pawn.collapsed = False

                    qutils.perform_standard_slide(self, source, target)

                self.classical_board[target.x][target.y] = pawn.copy()

        elif move_type == Pawn.MoveType.CAPTURE:
            #pawn is the only piece that needs to collapse target when capturing
            #because it can't move diagonally unless capturing
            self.collapse_by_flag(pawn.qflag | target_piece.qflag)

            if (
                self.classical_board[source.x][source.y] != NullPiece and
                self.classical_board[target.x][target.y] != NullPiece
            ):
                qutils.perform_capture_jump(self, source, target)

                self.classical_board[source.x][source.y] = NullPiece
                self.classical_board[target.x][target.y] = pawn.copy()

        elif move_type == Pawn.MoveType.EN_PASSANT:
            if target_piece == NullPiece:
                qutils.perform_standard_en_passant(self, source, target, ep_point)

                self.classical_board[source.x][source.y] = NullPiece
                self.classical_board[target.x][target.y] = pawn
                self.classical_board[ep_point.x][ep_point.y] = NullPiece

            elif target_piece.color == pawn.color:
                self.collapse_by_flag(target_piece.qflag)

                if self.classical_board[target.x][target.y] == NullPiece:
                    qutils.perform_standard_en_passant(self, source, target, ep_point)
                    
                    self.classical_board[source.x][source.y] = NullPiece
                    self.classical_board[target.x][target.y] = pawn.copy()
                    self.classical_board[ep_point.x][ep_point.y] = NullPiece
            else:
                self.collapse_by_flag(pawn.qflag)

                if self.classical_board[source.x][source.y] != NullPiece:
                    qutils.perform_capture_en_passant(self, source, target, ep_point)

                    self.classical_board[source.x][source.y] = NullPiece
                    self.classical_board[target.x][target.y] = pawn.copy()
                    self.classical_board[ep_point.x][ep_point.y] = NullPiece

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
            self.classical_board[target1.x][target1.y] = piece.copy()

        if target_piece2 == NullPiece:
            self.classical_board[target2.x][target2.y] = piece.copy()

        if target_piece1 == NullPiece and target_piece2 == NullPiece:
            self.classical_board[source.x][source.y] = new_source_piece.copy()

        self.set_piece_uncollapsed(target1)
        self.set_piece_uncollapsed(target2)
        self.set_piece_uncollapsed(source)
    
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
                piece1.collapsed = False
                new_source1_piece = piece1

            if self.entangle_path_flags(piece2.qflag, source2, target):
                piece2.collapsed = False
                new_source2_piece = piece2

        else:
            qutils.perform_merge_jump(self, source1, source2, target)

        #we should only entangle flags between the qubits to which we apply iswap_sqrt
        #TODO: find best way to do this        
        self.entangle_flags(piece1.qflag, piece2.qflag)
        self.entangle_flags(piece1.qflag, target_piece.qflag)

        self.classical_board[target.x][target.y] = piece1.copy()

        if target_piece == NullPiece:
            self.classical_board[source1.x][source1.y] = new_source1_piece.copy()
            self.classical_board[source2.x][source2.y] = new_source2_piece.copy()

        #unless both sources are collapsed and the target is empty, we can't
        #be sure the target is collapsed
        if target_piece == NullPiece and piece1.collapsed and piece2.collapsed:
            self.classical_board[target.x][target.y].collapsed = True
        else:        
            self.set_piece_uncollapsed(source1)
            self.set_piece_uncollapsed(source2)
            self.set_piece_uncollapsed(target)

    def castling_move(self, king_source, rook_source, king_target, rook_target):
        king = self.classical_board[king_source.x][king_source.y]
        rook = self.classical_board[rook_source.x][rook_source.y]

        king_target_piece = self.classical_board[king_target.x][king_target.y]
        rook_target_piece = self.classical_board[rook_target.x][rook_target.y]

        #collapse target pieces
        self.collapse_by_flag(king_target_piece.qflag | rook_target_piece.qflag)

        #if both targets are empty
        if (
            self.classical_board[king_target.x][king_target.y] == NullPiece and
            self.classical_board[rook_target.x][rook_target.y] == NullPiece
        ):
            #the path doesn't neccesarily have to be the shortest straight path
            #between king and rook
            king_path = self.qchess.get_path_points(king_source, king_target)
            rook_path = self.qchess.get_path_points(rook_source, rook_target)

            # in general it's the unique combination of their paths
            path = []
            for point in king_path + rook_path:
                if point == king_target or point == rook_target: continue

                #we don't need to include empty squares
                if self.classical_board[point.x][point.y] == NullPiece: continue

                if not point in path:
                    path.append(point)

            #exclude king_target and rook_target just in case
            if king_target in path: path.remove(king_target)
            if rook_target in path: path.remove(rook_target)

            #perform the quantum move        
            qutils.perform_castle(self, king_source, rook_source, king_target, rook_target, path)

            if not path:
                #remove from source only if path is empty
                self.classical_board[king_source.x][king_source.y] = NullPiece
                self.classical_board[rook_source.x][rook_source.y] = NullPiece
            else:
                #entangle with all the pieces in the path
                path_qflags = 0
                for point in path:
                    path_qflags |= self.classical_board[point.x][point.y].qflag
                
                self.entangle_flags(king.qflag, rook.qflag)
                self.entangle_flags(path_qflags, king.qflag)

                king.collapsed = False
                rook.collapsed = False

            self.classical_board[king_target.x][king_target.y] = king.copy()
            self.classical_board[rook_target.x][rook_target.y] = rook.copy()
