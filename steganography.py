import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, AncillaRegister
from qiskit import execute
from qiskit import Aer
from qiskit import IBMQ
from qiskit.compiler import transpile
from time import perf_counter
from qiskit.tools.visualization import plot_histogram
from qiskit.circuit.library import SXdgGate


import numpy as np
import neqr
import random
import math

'''
params
---------------
regY: a quantum register
regX: a quantum register
circuit: the circuit that contains all the register
result: an empty register that will hold results

return
---------------
a size 2 register, c0 c1:
If c1c0 = 00, then Y = X.
If c1c0 = 01, then Y < X.
If c1c0 = 10, then Y > X
'''
def comparator(regY, regX, circuit, result): 
    # regX and regY should have the same size 
    regLength = regX.size 
    ancilla = AncillaRegister(2*regLength)
    circuit.add_register(ancilla)

    circuit.x(ancilla)
    for index in range(regLength):
        circuit.x(regX[index])
        circuit.mcx([regY[index], regX[index]]+[ancilla[i] for i in range(2*index)], [ancilla[index*2]])
        if index < regLength-1: 
            circuit.mcx([regY[index], regX[index]]+[ancilla[i] for i in range(2*index)], [ancilla[2*regLength-2]])
        circuit.x(regX[index])
        circuit.x(regY[index])
        circuit.mcx([regY[index], regX[index]]+[ancilla[i] for i in range(2*index)], [ancilla[index*2+1]])
        if index < regLength-1: 
            circuit.mcx([regY[index], regX[index]]+[ancilla[i] for i in range(2*index)], [ancilla[2*regLength-1]])
        circuit.x(regY[index])     
    circuit.x(ancilla)

    circuit.cx(ancilla[2*regLength-2], result[0])
    circuit.cx(ancilla[2*regLength-1], result[1])

    return (circuit, result)


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
    
    return (circuit, result)


'''
params
---------------
Y: a quantum register
X: a quantum register
difference: an empty quantum register the same size as X and Y

return
---------------
A quantum register |D> which holds the positive difference of Y and X.
'''
def difference(circuit, Y, X, difference):
    # PART 1: 
    # reversible parallel subtractor
    
    # initialize registers to store sign, difference, and junk qubits
    regLength = X.size
    sign = QuantumRegister(1, 'sign')
    ancilla = QuantumRegister(regLength - 1, 'junk')
    circuit.add_register(ancilla)
    circuit.add_register(sign)

    # perform half subtractor for last qubit
    rev_half_subtractor(circuit, X[-1], Y[-1], difference[-1], ancilla[-1])
    
    # perform full subtrator for rest of qubits
    for i in range(regLength - 2, 0, -1): 
        rev_full_subtractor(circuit, X[i], Y[i], ancilla[i], difference[i], ancilla[i-1])
    rev_full_subtractor(circuit, X[0], Y[0], ancilla[0], difference[0], sign[0])
    
    # swap X and difference registers to fix result 
    # this is just sort of a thing you have to do
    for i in range(regLength - 1, -1, -1): 
        circuit.swap(difference[i], X[i])
    
    # PART 2: 
    # complementary operation

    # flip the difference based on the sign (pt 1)
    for i in range(regLength): 
        circuit.cx(sign[0], difference[i])
    
    # flip the difference again, but based on sign and remaining bits (pt 2)
    #for i in range(regLength-1, -1, -1):
    for i in range(regLength):
        circuit.mcx([sign[0]] + difference[i+1:], difference[i])
    



'''
params
---------------
regA: a quantum register, one of the numbers being subtracted
regB: a quantum register, one of the numbers being subtracted
Q: Updated depending on result
Borrow: Digit to be carried over

return
---------------
Performs A - B, and updates results into Q and Borrow 
'''
def rev_half_subtractor(circuit, A, B, Q, Borrow): 
    csxdg_gate = SXdgGate().control()
    circuit.append(csxdg_gate, [A, Borrow])
    circuit.cx(A, Q)
    circuit.cx(B, A)
    circuit.csx(B, Borrow)
    circuit.csx(A, Borrow)
    circuit.barrier()
    
    
'''
params
---------------
regA: a quantum register, one of the numbers being subtracted
regB: a quantum register, one of the numbers subtracting
regC: a quantum register, one of the numbers subtracting
Q: Updated depending on result
Borrow: Digit to be carried over

return
---------------
Performs A - B - C, updates results into Q and Borrow
'''
def rev_full_subtractor(circuit, A, B, C, Q, Borrow): 
    csxdg_gate = SXdgGate().control()
    circuit.append(csxdg_gate, [A, Borrow])
    circuit.cx(A, Q)
    circuit.cx(B, A)
    circuit.csx(B, Borrow)
    circuit.cx(C, A)
    circuit.csx(C, Borrow)
    circuit.csx(A, Borrow)
    circuit.barrier()


def controlled_difference(controlled_qubit, circuit, Y, X, difference): 
    # PART 1: 
    # reversible parallel subtractor
    
    # initialize registers to store sign, difference, and junk qubits
    regLength = X.size
    sign = QuantumRegister(1, 'sign')
    ancilla = QuantumRegister(regLength - 1, 'junk')
    circuit.add_register(ancilla)
    circuit.add_register(sign)

    # perform half subtractor for last qubit
    controlled_rhs(controlled_qubit, circuit, X[-1], Y[-1], difference[-1], ancilla[-1])
    
    # perform full subtrator for rest of qubits
    for i in range(regLength - 2, 0, -1): 
        controlled_rfs(controlled_qubit, circuit, X[i], Y[i], ancilla[i], difference[i], ancilla[i-1])
    controlled_rfs(controlled_qubit, circuit, X[0], Y[0], ancilla[0], difference[0], sign[0])
    
    # swap X and difference registers to fix result 
    # this is just sort of a thing you have to do
    for i in range(regLength - 1, -1, -1): 
        circuit.cswap(controlled_qubit, difference[i], X[i])
    
    # PART 2: 
    # complementary operation

    # flip the difference based on the sign (pt 1)
    for i in range(regLength): 
        circuit.ccx(controlled_qubit, sign[0], difference[i])
    
    # flip the difference again, but based on sign and remaining bits (pt 2)
    #for i in range(regLength-1, -1, -1):
    for i in range(regLength):
        circuit.mcx([controlled_qubit] + [sign[0]] + difference[i+1:], difference[i])
    

# controlled reversible half subtractor
def controlled_rhs(controlled_qubit, circuit, A, B, Q, Borrow): 
    # allocate ancilla qubits
    anc1 = QuantumRegister(3)
    circuit.add_register(anc1)

    # rewritten code to control for given qubit
    csxdg_gate = SXdgGate().control()
    circuit.ccx(controlled_qubit, A, anc1[0])
    circuit.append(csxdg_gate, [anc1[0], Borrow])
    circuit.ccx(controlled_qubit, A, Q)
    circuit.ccx(controlled_qubit, B, A)
    circuit.ccx(controlled_qubit, B, anc1[1])
    circuit.ccx(controlled_qubit, A, anc1[2])
    circuit.csx(anc1[1], Borrow)
    circuit.csx(anc1[2], Borrow)
    circuit.barrier()

# controlled reversible full subtractor
def controlled_rfs(controlled_qubit, circuit, A, B, C, Q, Borrow): 
    # allocate ancilla qubits
    anc2 = QuantumRegister(4)
    circuit.add_register(anc2)
    
    # rewritten code to control for given qubit
    csxdg_gate = SXdgGate().control()
    circuit.ccx(controlled_qubit, A, anc2[0])
    circuit.append(csxdg_gate, [anc2[0], Borrow])
    circuit.cx(A, Q)
    circuit.cx(B, A)
    circuit.ccx(controlled_qubit, B, anc2[1])
    circuit.csx(anc2[1], Borrow)
    circuit.cx(C, A)
    circuit.ccx(controlled_qubit, C, anc2[2])
    circuit.csx(anc2[2], Borrow)
    circuit.ccx(controlled_qubit, A, anc2[3])
    circuit.csx(anc2[3], Borrow)
    circuit.barrier()

'''
Embedding Procedure
'''

'''
params
------------------
k: the number of binary images
binary_images: a list of 2^n by 2^n binary images to construct the secret image
assume they are all the same size

return
-------------------
the secret image
'''
def get_secret_image(k, binary_images):
    n = len(binary_images[0][0])
    secret_image = [['' for i in range(n)] for j in range(n)]
    for i in range(k):
        for j in range(n):
            for l in range(n):
                secret_image[j][l] += str(binary_images[i][j][l])
    return secret_image


'''
params
--------------------
secret_image: a quantum circuit containing the secret image

returns
--------------------
nothing
'''
def invert(secret_image):
    for i in range(secret_image.num_qubits):
        secret_image.x(i)


'''
params
------------------
cover_image: the quantum cover image
secret_image: the quantum secret image
image_size: size of the image

return
------------------
key: the quantum key
'''
def get_key(cover_image, secret_image, image_size):
    key = QuantumCircuit(image_size)


def embed(circuit, C, S, Key):
    ### PART ONE
    
    _, r_1 = coordinate_comparator(circuit, C, S)
    _, r_2 = coordinate_comparator(circuit, C, Key)

    ### PART FOUR
    # placeholder code to declare variables so 
    # vs code won't get all uppity
    cover_image_values = QuantumRegister(1) # not real size
    secret_image_values = QuantumRegister(1) # not real size
    comparator_result = QuantumRegister(2)
    circuit.add_register(cover_image_values)
    circuit.add_register(secret_image_values)
    circuit.add_register(comparator_result)

    # this is part of the actual code now

    key_i = QuantumRegister(1, 'key_i')
    circuit.add_register(key_i)

    # flip for zero-controlled ccnots
    circuit.x(comparator_result[1])
    circuit.ccx(r_1, comparator_result[1], cover_image_values)
    circuit.ccx(r_1, comparator_result[1], secret_image_values)
    circuit.x(comparator_result[1]) # flip back

    # do a cute little toffoli cascade for the cccswap and cccx
    anc = QuantumRegister(2) # allocate ancilla qubits
    circuit.add_register(anc)
    circuit.ccx(r_1, r_2, anc[0])
    circuit.ccx(anc[0], comparator_result[1], anc[1])
    circuit.cswap(anc[2], cover_image_values, secret_image_values) # cccswap
    circuit.cx(comparator_result[1], key_i[0]) # cccnot



