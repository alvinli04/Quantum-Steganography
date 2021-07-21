import qiskit

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import Aer
from qiskit import IBMQ
from qiskit.compiler import transpile
from time import perf_counter
from qiskit.tools.visualization import plot_histogram

import numpy as np



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
            ret.append([0 for i in range(8 - len(bitstring))] + [1 if c=='1' else 0 for c in bitstring])
    return ret


'''
params
----------------
bitStr: a representation of an image using bitstrings to represent grayscale values

return
----------------
A quantum circuit containing the NEQR representation of the image
'''
def neqr(bitStr): 
    newBitStr = bitStr

    #print(newBitStr)
    #print("\n")

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
    print("Number of Qubits:", numOfQubits)

    # -----------------------------------
    # Drawing the Quantum Circuit
    # -----------------------------------
    lengthIntensity = intensity.size
    lengthIdx = idx.size

    quantumImage.i([intensity[lengthIntensity-1-i] for i in range(lengthIntensity)])
    quantumImage.h([idx[lengthIdx-1-i] for i in range(lengthIdx)])

    numOfPixels = len(newBitStr)

    for i in range(numOfPixels):
        # X-gate (enabling zero-controlled nature)
        if i==2: 
            quantumImage.x(idx[0])
        if i==1: 
            quantumImage.x(idx[1])
        if i==0:
            quantumImage.x(idx)

        # Configuring CCNOT (ccx) gates with control and target qubits
        for j in range(len(newBitStr[i])):
            if newBitStr[i][j] == 1:
                quantumImage.ccx(idx[0], idx[1], intensity[lengthIntensity-1-j])
        
        # X-gate (enabling zero-controlled nature)
        if i==2: 
            quantumImage.x(idx[0])
        if i==1: 
            quantumImage.x(idx[1])
        if i==0:
            quantumImage.x(idx)
        quantumImage.barrier()

    #quantumImage.measure(range(10), range(10))

    #backend = Aer.get_backend('qasm_simulator')
    #job = execute(quantumImage, backend, shots=1024) # shots default = 1024
    #result = job.result()
    #print(result.get_counts()) 

    return quantumImage

if __name__ == '__main__':
    test_picture_2x2 = [[0, 100], [200, 255]]
    arr = convert_to_bits(test_picture_2x2)
    print(arr, "\n")
    print(neqr(arr))
