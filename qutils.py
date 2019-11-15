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

def perform_capture_jump(board, source, target):
    qsource = board.get_qubit(source.x, source.y)
    qtarget = board.get_qubit(target.x, target.y)

    #this ancilla qubit is going to hold the captured piece
    captured_piece = board.aregister[0]
    board.qcircuit.reset(captured_piece)

    board.qcircuit.unitary(iSwap, [qtarget, captured_piece], label='iSwap')
    board.qcircuit.unitary(iSwap, [qsource, qtarget], label='iSwap')

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