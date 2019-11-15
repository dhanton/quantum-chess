import numpy as np

from qiskit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info.operators import Operator
from qiskit import Aer
from qiskit import execute
from qiskit.tools.visualization import plot_histogram

backend = Aer.get_backend('qasm_simulator')

iSwap = Operator([
    [1, 0, 0, 0],
    [0, 0, 1j, 0],
    [0, 1j, 0, 0],
    [0, 0, 0, 1],
])

iSwap_sqrt = Operator([
    [1, 0, 0, 0],
    [0, 1/np.sqrt(2), 1j/np.sqrt(2), 0],
    [0, 1j/np.sqrt(2), 1/np.sqrt(2), 0],
    [0, 0, 0, 1],
])

def perform_standard_jump(board, source, target):
    qsource = board.get_qubit(source.x, source.y)
    qtarget = board.get_qubit(target.x, target.y)

    board.qcircuit.unitary(iSwap, [qsource, qtarget], label='iSwap')

def perform_blocked_jump(board, source, target):
    qsource = board.get_qubit(source.x, source.y)
    qtarget = board.get_qubit(target.x, target.y)

    #get the ancilla qubit and set it to |0>
    ancilla = board.aregister[0]
    board.qcircuit.reset(ancilla)
    
    board.qcircuit.x(qtarget)
    board.qcircuit.cx(qtarget, ancilla)
    board.qcircuit.x(qtarget)

    board.qcircuit.measure(ancilla, board.cregister[0])

    #perform quantum move only if no piece is blocking
    board.qcircuit.unitary(iSwap, [qsource, qtarget], label='iSwap').c_if(board.cregister, 1)

    result = execute(board.qcircuit, backend=backend, shots=1).result()
    
    #read the value of the classical bit after execution
    #TODO: Obtain this value in a more elegant way
    #      Right now it ONLY works when shots=1
    cbit_value = int(list(result.get_counts().keys())[0])

    return (cbit_value == 1)

def perform_capture_jump(board, source, target):
    qsource = board.get_qubit(source.x, source.y)
    qtarget = board.get_qubit(target.x, target.y)

    #get the ancilla qubit and reset it to |0>
    ancilla = board.aregister[0]
    board.qcircuit.reset(ancilla)

    #this other ancilla is gonna be used to hold the captured piece
    captured_piece = board.aregister[1]
    board.qcircuit.reset(captured_piece)

    board.qcircuit.cx(qsource, ancilla)

    board.qcircuit.measure(ancilla, board.cregister[0])

    #perform quantum move if capturing piece is in source
    board.qcircuit.unitary(iSwap, [qtarget, captured_piece], label='iSwap').c_if(board.cregister, 1)
    board.qcircuit.unitary(iSwap, [qsource, qtarget], label='iSwap').c_if(board.cregister, 1)

    result = execute(board.qcircuit, backend=backend, shots=1).result()
    cbit_value = int(list(result.get_counts().keys())[0])

    return (cbit_value == 1)

def perform_split_jump(board, source, target1, target2):
    qsource = board.get_qubit(source.x, source.y)
    qtarget1 = board.get_qubit(target1.x, target1.y)
    qtarget2 = board.get_qubit(target2.x, target2.y)

    board.qcircuit.unitary(iSwap_sqrt, [qtarget1, qsource], label='iSwap_sqrt')
    board.qcircuit.unitary(iSwap, [qsource, qtarget2], label='iSwap')

def perform_merge_jump(board, source1, source2, target):
    qsource1 = board.get_qubit(source1.x, source1.y)
    qsource2 = board.get_qubit(source2.x, source2.y)
    qtarget = board.get_qubit(target.x, target.y)

    board.qcircuit.unitary(iSwap, [qtarget, qsource2], label='iSwap')
    board.qcircuit.unitary(iSwap_sqrt, [qsource1, qtarget], label='iSwap_sqrt')