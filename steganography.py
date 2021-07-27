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


'''
params
---------------
YX: a quantum register containing two coordinates, |Y>|X>
AB: a quantum register containing two coordinates, |A>|B>

return
---------------
A single qubit |r> which is |1> when YX = AB and |0> otherwise
'''
def coordinate_comparator(circuit, result, YX, AB):
    assert len(YX) == len(AB)
    n = YX.size
    
    for i in range(n):
        circuit.x(YX[i])
        circuit.cx(YX[i], AB[i])
        circuit.x(YX[i])
        
    circuit.mcx(AB, result)
    
    for i in range(n):
        circuit.x(YX[i])
        circuit.cx(YX[i], AB[i])
        circuit.x(YX[i])


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
    assert len(Y) == len(X)
    # PART 1: 
    # reversible parallel subtractor
    
    # initialize registers to store sign, difference, and junk qubits
    regLength = X.size
    sign = QuantumRegister(1)
    ancilla = QuantumRegister(regLength - 1)
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
intensity: a quantum register in secret_image that contains the intensity

returns
--------------------
nothing
'''
def invert(secret_image, intensity, inverse):
    secret_image.x(intensity)
    for i in range(len(intensity)):
        secret_image.cx(intensity[i], inverse[i])
    secret_image.x(intensity)


'''
params
------------------
circuit: the quantum circuit containing all the images
key: an empty key register, to be modified
cover: the quantum cover image
secret: the quantum secret image
inv_secret: the inverse secret image
image_size: total size of the image
diff1: holds difference between cover and secret
diff2: holds difference between cover and inverse secret
image_size: number of pixels
'''
def get_key(circuit, 
            key_idx, 
            key_result,
            cover_intensity,  
            secret_intensity, 
            inv_secret_intensity, 
            diff1, 
            diff2, 
            comp_result,
            image_size):

    circuit.h(key_idx)

    difference(circuit, cover_intensity, secret_intensity, diff1)
    difference(circuit, cover_intensity, inv_secret_intensity, diff2)

    comparator(diff1, diff2, circuit, comp_result)

    circuit.x(comp_result[1])

    for i in range(image_size):
        bin_ind = bin(i)[2:]
        bin_ind = (len(key_idx) - len(bin_ind)) * '0' + bin_ind
        bin_ind = bin_ind[::-1]

        # X-gate (enabling zero-controlled nature)
        for j in range(len(bin_ind)):
            if bin_ind[j] == '0':
                circuit.x(key_idx[j])

        circuit.mcx(comp_result[:] + key_idx[:], key_result)
        
        # X-gate (enabling zero-controlled nature)
        for j in range(len(bin_ind)):
            if bin_ind[j] == '0':
                circuit.x(key_idx[j])

    circuit.x(comp_result[1])

def embed(circuit, C, S, Key, cover_image_values, secret_image_values, key_i):
    # removed code. can be used for unit test
    '''
    #preperation
    array = [[random.randint(0, 255), random.randint(0, 255)], [random.randint(0, 255), random.randint(0, 255)]]
    print(array)
    bits_array = neqr.convert_to_bits(array)
    print(bits_array)

    #setting up the images, difference registers, and circuiit
    _, cover_image_values = neqr.neqr(bits_array)
    _, secret_image_values = neqr.neqr(bits_array)
    circuit = QuantumCircuit(cover_image_values, secret_image_values, difference_1, difference_2)
    '''
    #part 1:
    #carrying out the coordinate comparators 
    coord_result = QuantumRegister(2, 'coord_result')
    circuit.add_register(coord_result)
    coordinate_comparator(circuit, coord_result, C, S)

    #getting the key through getKey (once its done)
    coordinate_comparator(circuit, coord_result, C, Key)

    #adding outputs to the circuit 
    circuit.add_register(coord_result[0])
    circuit.add_register(coord_result[1])

    #part 2: 
    #need to make a controlled difference method :(
    diff1_result = QuantumRegister(C.size, 'diff1_result')
    circuit.add_register(diff1_result)
    controlled_difference(coord_result[0], circuit, cover_image_values, secret_image_values, diff1_result)

    #after this, secret_image_values are inverted 
    invert(circuit, secret_image_values)
    #computing difference again
    diff2_result = QuantumRegister(C.size, 'diff2_result')
    circuit.add_register(diff2_result)
    difference(circuit,cover_image_values, secret_image_values, diff2_result)

    #comparing the differences
    comparator_result = QuantumRegister(2, "compare_result")
    circuit.add_register(comparator_result)
    comparator(circuit, diff2_result, diff1_result, comparator_result)

    # flip for zero-controlled ccnots
    circuit.x(comparator_result[1])
    circuit.ccx(coord_result[0], comparator_result[1], cover_image_values)
    circuit.ccx(coord_result[0], comparator_result[1], secret_image_values)
    circuit.x(comparator_result[1]) # flip back

    # do a cute little toffoli cascade for the cccswap and cccx
    anc = QuantumRegister(2) # allocate ancilla qubits
    circuit.add_register(anc)
    circuit.ccx(coord_result[0], coord_result[1], anc[0])
    circuit.ccx(anc[0], comparator_result[1], anc[1])
    circuit.cswap(anc[2], cover_image_values, secret_image_values) # cccswap
    circuit.cx(comparator_result[1], key_i) # cccnot


def extract(circuit, key_idx, key_val, cs_idx, cs_val, extracted, comp_result, k):
    for i in range(k):
        circuit.cx(cs_val[len(cs_val) - k - 1 + i], extracted[i])

    coordinate_comparator(circuit, comp_result, key_idx, cs_idx)

    for i in range(image_size):
        bin_ind = bin(i)[2:]
        bin_ind = (len(key_idx) - len(bin_ind)) * '0' + bin_ind
        bin_ind = bin_ind[::-1]

        # X-gate (enabling zero-controlled nature)
        for j in range(len(bin_ind)):
            if bin_ind[j] == '0':
                circuit.x(cs_idx[j])

        circuit.mcx(comp_result[:] + cs_idx[:], extracted)
        
        # X-gate (enabling zero-controlled nature)
        for j in range(len(bin_ind)):
            if bin_ind[j] == '0':
                circuit.x(cs_idx[j])

