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
    
def comparator(regX, regY): 
    qc = QuantumCircuit(regX, regY)
    # regX and regY should have the same size 
    regLength = regX.size 
    ancilla = AncillaRegister(2)
    qc.add_register(ancilla)

    for index in range(regLength): 
        qc.x(regY[index])
        #qc.ccx(regY[index], regX[index], ancilla[0])
        print("anc: ", ancilla, "\n")
        qc.x(regY[index])
        qc.x(regX[index])
        #qc.ccx(regY[index], regX[index], ancilla[1])
    return ancilla

if __name__ == '__main__':
    regX = QuantumRegister(2)
    regY = QuantumRegister(2)
    cResult = comparator(regX, regY)
    print("Comparator Register Output")
    #print("c0: ", cResult[0], "c1: ", cResult[1], "\n")

        

