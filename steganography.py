import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import Aer
from qiskit import IBMQ
from qiskit.compiler import transpile
from time import perf_counter
from qiskit.tools.visualization import plot_histogram

import numpy as np
import neqr
import random
import math

'''
params
---------------
Y: a quantum register
X: a quantum register

return
---------------
a size 2 register, c0 c1:
If c1c0 = 00, then Y = X.
If c1c0 = 01, then Y < X.
If c1c0 = 10, then Y > X
'''
def comparator_test(Y, X):
    pass


'''
params
---------------
YX: a quantum register containing two coordinates, |Y>|X>
AB: a quantum register containing two coordinates, |A>|B>

return
---------------
A single qubit |r> which is |1> when YX = AB and |0> otherwise
'''
def coordinate_comparator(circuit, YX, AB):
    n = YX.size
    result = QuantumRegister(1, 'result')
    circuit.add_register(result)
    
    for i in range(n):
        circuit.x(YX[i])
        circuit.cx(YX[i], AB[i])
        circuit.x(YX[i])
        
    circuit.mcx(AB, result)
    
    for i in range(n):
        circuit.x(YX[i])
        circuit.cx(YX[i], AB[i])
        circuit.x(YX[i])
    
    return circuit


'''
params
---------------
Y: a quantum register
X: a quantum register

return
---------------
A quantum register |D> which holds the positive difference of Y and X.
'''
def difference(Y, X):
    pass
