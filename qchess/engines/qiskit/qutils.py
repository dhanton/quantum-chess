import math

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info.operators import Operator
from qiskit import Aer
from qiskit import execute
from qiskit.tools.visualization import plot_histogram

backend = Aer.get_backend('qasm_simulator')

b = math.sqrt(2)

iSwap = Operator([
    [1, 0, 0, 0],
    [0, 0, 1j, 0],
    [0, 1j, 0, 0],
    [0, 0, 0, 1],
])

#when the controlled qubit holds if a path is clear
#then this gate can be understood as the slide gate
iSwap_controlled = Operator([
    [1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1j, 0, 0, 0, 0, 0],
    [0, 1j, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],
])

iSwap_sqrt = Operator([
    [1, 0, 0, 0],
    [0, 1/b, 1j/b, 0],
    [0, 1j/b, 1/b, 0],
    [0, 0, 0, 1],
])

#in base s, t, control
iSwap_sqrt_controlled = Operator([
    [1, 0, 0, 0, 0, 0, 0, 0],
    [0, 1/b, 1j/b, 0, 0, 0, 0, 0],
    [0, 1j/b, 1/b, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1],

])

def perform_standard_jump(engine, source, target):
    qsource = engine.get_qubit(source.x, source.y)
    qtarget = engine.get_qubit(target.x, target.y)

    engine.qcircuit.unitary(iSwap, [qsource, qtarget], label='iSwap')

def perform_capture_jump(engine, source, target):
    qsource = engine.get_qubit(source.x, source.y)
    qtarget = engine.get_qubit(target.x, target.y)

    #this ancilla qubit is going to hold the captured piece
    captured_piece = engine.aregister[0]
    engine.qcircuit.reset(captured_piece)

    engine.qcircuit.unitary(iSwap, [qtarget, captured_piece], label='iSwap')
    engine.qcircuit.unitary(iSwap, [qsource, qtarget], label='iSwap')

def perform_split_jump(engine, source, target1, target2):
    qsource = engine.get_qubit(source.x, source.y)
    qtarget1 = engine.get_qubit(target1.x, target1.y)
    qtarget2 = engine.get_qubit(target2.x, target2.y)

    engine.qcircuit.unitary(iSwap_sqrt, [qtarget1, qsource], label='iSwap_sqrt')
    engine.qcircuit.unitary(iSwap, [qsource, qtarget2], label='iSwap')

def perform_merge_jump(engine, source1, source2, target):
    qsource1 = engine.get_qubit(source1.x, source1.y)
    qsource2 = engine.get_qubit(source2.x, source2.y)
    qtarget = engine.get_qubit(target.x, target.y)

    engine.qcircuit.unitary(iSwap, [qtarget, qsource2], label='iSwap')
    engine.qcircuit.unitary(iSwap_sqrt, [qsource1, qtarget], label='iSwap_sqrt')

def perform_standard_slide(engine, source, target):
    control_qubits = []

    for point in engine.qchess.get_path_points(source, target):
        control_qubits.append(engine.get_qubit(point.x, point.y))
        engine.qcircuit.x(engine.get_qubit(point.x, point.y))

    qsource = engine.get_qubit(source.x, source.y)
    qtarget = engine.get_qubit(target.x, target.y)
    
    path_ancilla = engine.aregister[0]
    engine.qcircuit.reset(path_ancilla)
    engine.qcircuit.x(path_ancilla)

    engine.qcircuit.mct(control_qubits, path_ancilla, engine.mct_register, mode='advanced')
    engine.qcircuit.unitary(iSwap_controlled, [qsource, qtarget, path_ancilla])

    for point in engine.qchess.get_path_points(source, target):
        engine.qcircuit.x(engine.get_qubit(point.x, point.y))

"""
    *The source piece has already been collapsed before this is called*

    So the basic idea behind this circuit is that if:
        -The path is clear (doesn't matter if target is empty or not)
                        OR
        -The path is not clear but the target is empty

    Then there's no double occupancy and the piece can capture.
"""
def perform_capture_slide(engine, source, target):
    control_qubits = []

    for point in engine.qchess.get_path_points(source, target):
        control_qubits.append(engine.get_qubit(point.x, point.y))
        engine.qcircuit.x(engine.get_qubit(point.x, point.y))

    qsource = engine.get_qubit(source.x, source.y)
    qtarget = engine.get_qubit(target.x, target.y)

    #holds if the path is clear or not
    path_ancilla = engine.aregister[0]
    engine.qcircuit.reset(path_ancilla)
    engine.qcircuit.x(path_ancilla)

    engine.qcircuit.mct(control_qubits, path_ancilla, engine.mct_register, mode='advanced')

    #holds the final condition that's going to be measured
    cond_ancilla = engine.aregister[1]
    engine.qcircuit.reset(cond_ancilla)

    #holds the captured piece
    captured_piece = engine.aregister[2]
    engine.qcircuit.reset(captured_piece)

    #path is not blocked
    engine.qcircuit.x(path_ancilla)
    engine.qcircuit.cx(path_ancilla, cond_ancilla)
    engine.qcircuit.x(path_ancilla)

    #blocked but target empty
    engine.qcircuit.x(qtarget)
    engine.qcircuit.ccx(qtarget, path_ancilla, cond_ancilla)
    engine.qcircuit.x(qtarget)

    engine.qcircuit.measure(cond_ancilla, engine.cbit_misc[0])

    engine.qcircuit.unitary(iSwap_controlled, [qtarget, captured_piece, path_ancilla]).c_if(engine.cbit_misc, 1)
    engine.qcircuit.unitary(iSwap_controlled, [qsource, qtarget, path_ancilla]).c_if(engine.cbit_misc, 1)

    for qubit in control_qubits:
        engine.qcircuit.x(qubit)

    result = execute(engine.qcircuit, backend=backend, shots=1).result()

    #since get_counts() gives '1 00000001'
    #a bit hacky but I don't know any other way to get this result
    cbit_value = int(list(result.get_counts().keys())[0].split(' ')[0])

    return (cbit_value == 1)

"""
    Since the differences between both operations are only two gates,
    it's useful to implement them together.

    The args (single, double1, double2) are
        split: (source, target1, target2)
        merge: (target, source1, source2)
"""
def _slide_split_merge(engine, single, double1, double2, is_split):
    qsingle = engine.get_qubit(single.x, single.y)
    qdouble1 = engine.get_qubit(double1.x, double1.y)
    qdouble2 = engine.get_qubit(double2.x, double2.y)

    #get all qubits in first path
    control_qubits1 = []
    for point in engine.qchess.get_path_points(single, double1):
        control_qubits1.append(engine.get_qubit(point.x, point.y))
        engine.qcircuit.x(engine.get_qubit(point.x, point.y))

    #holds if the first path is clear or not
    path_ancilla1 = engine.aregister[0]
    engine.qcircuit.reset(path_ancilla1)
    engine.qcircuit.x(path_ancilla1)

    #perform their combined CNOT 
    engine.qcircuit.mct(control_qubits1, path_ancilla1, engine.mct_register, mode='advanced')

    #undo the X
    for qubit in control_qubits1:
        engine.qcircuit.x(qubit)

    #get all qubits in second path
    control_qubits2 = []
    for point in engine.qchess.get_path_points(single, double2):
        control_qubits2.append(engine.get_qubit(point.x, point.y))
        engine.qcircuit.x(engine.get_qubit(point.x, point.y))

    #holds if the second path is clear or not
    path_ancilla2 = engine.aregister[1]
    engine.qcircuit.reset(path_ancilla2)
    engine.qcircuit.x(path_ancilla2)

    #perform their combined CNOT
    engine.qcircuit.mct(control_qubits2, path_ancilla2, engine.mct_register, mode='advanced')

    for qubit in control_qubits2:
        engine.qcircuit.x(qubit)

    #holds the control for jump and slide
    control_ancilla = engine.aregister[2]
    engine.qcircuit.reset(control_ancilla)
    engine.qcircuit.x(control_ancilla)

    #perform the split/merge
    engine.qcircuit.x(path_ancilla1)
    engine.qcircuit.x(path_ancilla2)
    engine.qcircuit.ccx(path_ancilla1, path_ancilla2, control_ancilla)

    if is_split:
        engine.qcircuit.unitary(iSwap_sqrt_controlled, [qdouble1, qsingle, control_ancilla])
        engine.qcircuit.unitary(iSwap_controlled, [qsingle, qdouble2, control_ancilla])
    else:
        engine.qcircuit.unitary(iSwap_controlled, [qsingle, qdouble2, control_ancilla])
        engine.qcircuit.unitary(iSwap_sqrt_controlled, [qdouble1, qsingle, control_ancilla])

    engine.qcircuit.x(path_ancilla1)
    engine.qcircuit.x(path_ancilla2)

    #reset the control
    engine.qcircuit.reset(control_ancilla)
    engine.qcircuit.x(control_ancilla)

    #perform one jump
    engine.qcircuit.x(path_ancilla1)
    engine.qcircuit.ccx(path_ancilla1, path_ancilla2, control_ancilla)
    engine.qcircuit.unitary(iSwap_controlled, [qdouble1, qsingle, control_ancilla])
    engine.qcircuit.x(path_ancilla1)

    #reset the control
    engine.qcircuit.reset(control_ancilla)
    engine.qcircuit.x(control_ancilla)

    #perform the other jump
    engine.qcircuit.x(path_ancilla2)
    engine.qcircuit.ccx(path_ancilla1, path_ancilla2, control_ancilla)
    engine.qcircuit.unitary(iSwap_controlled, [qsingle, qdouble2, control_ancilla])
    engine.qcircuit.x(path_ancilla2)

def perform_split_slide(engine, source, target1, target2):
    _slide_split_merge(engine, source, target1, target2, is_split=True)

def perform_merge_slide(engine, source1, source2, target):
    _slide_split_merge(engine, target, source1, source2, is_split=False)    

def perform_standard_en_passant(engine, source, target, ep_target):
    qsource = engine.get_qubit(source.x, source.y)
    qtarget = engine.get_qubit(target.x, target.y)
    qep_target = engine.get_qubit(ep_target.x, ep_target.y)

    captured_ancilla = engine.aregister[0]
    engine.qcircuit.reset(captured_ancilla)

    #holds if both source and ep_target are empty or not at the same time
    both_pieces_ancilla = engine.aregister[1]
    engine.qcircuit.reset(both_pieces_ancilla)

    engine.qcircuit.ccx(qsource, qep_target, both_pieces_ancilla)
    engine.qcircuit.x(both_pieces_ancilla)

    engine.qcircuit.unitary(iSwap_controlled, [qep_target, captured_ancilla, both_pieces_ancilla])
    engine.qcircuit.unitary(iSwap_controlled, [qsource, qtarget, both_pieces_ancilla])

def perform_capture_en_passant(engine, source, target, ep_target):
    qsource = engine.get_qubit(source.x, source.y)
    qtarget = engine.get_qubit(target.x, target.y)
    qep_target = engine.get_qubit(ep_target.x, ep_target.y)

    #since this move can capture two pieces at the same time,
    #we need two ancillas to hold them
    captured_ancilla1 = engine.aregister[0]
    engine.qcircuit.reset(captured_ancilla1)

    captured_ancilla2 = engine.aregister[1]
    engine.qcircuit.reset(captured_ancilla2)

    #holds if any of target, ep_target exist
    #Note: It's impossible for them to exist at the same time (during this function's call),
    #   since if they did that would mean that target piece has reached its position
    #   after the pawn moved and thus EP would not be not a valid move.
    any_piece_ancilla = engine.aregister[2]
    engine.qcircuit.reset(any_piece_ancilla)

    engine.qcircuit.cx(qep_target, any_piece_ancilla)
    engine.qcircuit.cx(qtarget, any_piece_ancilla)

    engine.qcircuit.x(any_piece_ancilla)

    engine.qcircuit.unitary(iSwap_controlled, [qep_target, captured_ancilla1, any_piece_ancilla])
    engine.qcircuit.unitary(iSwap_controlled, [qtarget, captured_ancilla2, any_piece_ancilla])
    engine.qcircuit.unitary(iSwap_controlled, [qsource, qtarget, any_piece_ancilla])

#path holds all points that must be empty for the move to be valid (excluding targets)
def perform_castle(engine, king_source, rook_source, king_target, rook_target, path=None):
    qking_source = engine.get_qubit(king_source.x, king_source.y)
    qrook_source = engine.get_qubit(rook_source.x, rook_source.y)
    qking_target = engine.get_qubit(king_target.x, king_target.y)
    qrook_target = engine.get_qubit(rook_target.x, rook_target.y)

    if path:
        #holds all the qubits of the path
        control_qubits = []
        for point in path:
            control_qubits.append(engine.get_qubit(point.x, point.y))
            engine.qcircuit.x(engine.get_qubit(point.x, point.y))

        #holds if the path is empty or not
        path_ancilla = engine.aregister[0]
        engine.qcircuit.reset(path_ancilla)
        engine.qcircuit.x(path_ancilla)

        engine.qcircuit.mct(control_qubits, path_ancilla, engine.mct_register, mode='advanced')

        #undo the x
        for qubit in control_qubits:
            engine.qcircuit.x(qubit)

        #perform the movement
        engine.qcircuit.unitary(iSwap_controlled, [qking_source, qking_target, path_ancilla])
        engine.qcircuit.unitary(iSwap_controlled, [qrook_source, qrook_target, path_ancilla])
    else:
        #perform the movement
        engine.qcircuit.unitary(iSwap, [qking_source, qking_target])
        engine.qcircuit.unitary(iSwap, [qrook_source, qrook_target])