import qiskit
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import Aer
from qiskit import IBMQ
from qiskit.circuit.quantumregister import AncillaRegister

def comparator(regX, regY): 
    qc = QuantumCircuit(regX, regY)
    # regX and regY should have the same size 
    regLength = regX.size 
    ancilla = AncillaRegister(2*regLength)
    qc.add_register(ancilla)
    qc.x(ancilla)
    for index in range(regLength):
        qc.x(regX[index])
        qc.mcx([regY[index], regX[index]]+[ancilla[i] for i in range(2*index)], [ancilla[index*2]])
        if index < regLength-1: 
            qc.mcx([regY[index], regX[index]]+[ancilla[i] for i in range(2*index)], [ancilla[2*regLength-2]])
        qc.x(regX[index])
        qc.x(regY[index])
        qc.mcx([regY[index], regX[index]]+[ancilla[i] for i in range(2*index)], [ancilla[index*2+1]])
        if index < regLength-1: 
            qc.mcx([regY[index], regX[index]]+[ancilla[i] for i in range(2*index)], [ancilla[2*regLength-1]])
        qc.x(regY[index])
        
    qc.x(ancilla)
    return qc

if __name__ == '__main__':
    regX = QuantumRegister(2, "x")
    regY = QuantumRegister(2, "y")
    cResult = comparator(regX, regY)
    print("Comparator Register Output")
    print(comparator(regX, regY))
