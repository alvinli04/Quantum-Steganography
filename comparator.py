import qiskit

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import Aer
from qiskit import IBMQ
from qiskit.circuit.quantumregister import AncillaRegister
from qiskit.compiler import transpile
from time import perf_counter
from qiskit.tools.visualization import plot_histogram

import numpy as np

def compare (register, c):
    if register[0] > register[1]: 
        c[0] = 1
        c[1] = 0
    elif register[0] < register[1]: 
        c[0] = 0
        c[1] = 1
    elif register[0] == register[1]:
        c[0] = 0
        c[1] = 0
        print("continuing")
    return c
    

def comparator(dregX, dregY): 
    qc = QuantumCircuit(dregX, dregY)
    # dregX and dregY should have the same size 
    dregLength = dregX.size() 
    ancilla = AncillaRegister(2)
    c = QuantumRegister(2)
    for index in range(dregLength): 
        qc.x(dregY[index])
        qc.ccx(dregY[index], dregX[index], ancilla[0])
        c = compare(ancilla, c)
        if c[0] != c[1]: 
            return c
        qc.x(dregY[index])
        qc.x(dregX[index])
        qc.ccx(dregY[index], dregX[index], ancilla[1])
        c = compare(ancilla, c)
        if c[0] != c[1]: 
            return c

    return c

if __name__ == '__main__':
    regX = QuantumRegister(2)
    regY = QuantumRegister(2)
    cResult = comparator(regX, regY)
    print("Comparator Register Output")
    print("c0: ", cResult[0], "c1: ", cResult[1], "\n")
        

