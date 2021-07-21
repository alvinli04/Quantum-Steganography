from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import Aer
from qiskit import IBMQ
from qiskit.compiler import transpile
from time import perf_counter

import numpy as np



test_picture_2x2 = [[0, 100], [200, 255]]

'''
params
---------------
picture: square 2d array of integers representing grayscale values
assume the length (n) is some power of 2

return
---------------
a flattened representation of picture using bitstrings (boolean arrays)
'''
def convert_to_bits (picture):
    n = len(picture)
    ret = []
    for i in range(n):
        for j in range(n):
            value = picture[i][j]
            bitstring = bin(value)[2:]
            ret.append([False for i in range(8 - len(bitstring))] + [True if c=='1' else False for c in bitstring])
    return ret


'''
params
----------------
bitStr: a representation of an image using bitstrings to represent grayscale values

return
----------------
A quantum circuit containing the NEQR representation of the image
'''
def quantum_sub_procedure(bitStr): 
    newBitStr = []
    for item in bitStr:
        if item:
            newBitStr.append(1)
        else:
            newBitStr.append(0)

    # Pixel position
    idx = QuantumRegister(2, 'idx')

    # Pixel intensity values
    intensity = QuantumRegister(8, 'intensity')

    # Classical Register
    creg = ClassicalRegister(10, 'creg')

    # Quantum Image Representation as a quantum circuit
    # with Pixel Position and Intensity registers
    quantumImage = QuantumCircuit(intensity, idx, creg)

    numOfQubits = quantumImage.num_qubits

    quantumImage.draw()
    print("Number of Qubits: {numOfQubits}")

    # -----------------------------------
    # Drawing the Quantum Circuit
    # -----------------------------------
    lengthIntensity = intensity.size
    lengthIdx = idx.size

    quantumImage.i([intensity[lengthIntensity-1-i] for i in range(lengthIntensity)])
    quantumImage.h([idx[lengthIdx-1-i] for i in range(lengthIdx)])

    quantumImage.barrier()

    numOfBits = 4; 

    for i in range(numOfQubits):
        if i==0 or i==1 : quantumImage.x(idx[i])

        if newBitStr[i] == 1:
            quantumImage.ccx(idx[0], idx[1], intensity[i])


    quantumImage.x([idx[lengthIdx-1-i] for i in range(lengthIdx)])

    quantumImage.barrier()
    # quantumImage.measure(range(10), range(10))
    quantumImage.draw()
    return quantumImage

if __name__ == '__main__':
    print('hello')
