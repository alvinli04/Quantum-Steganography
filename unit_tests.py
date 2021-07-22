from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import Aer
from qiskit import IBMQ
from qiskit.compiler import transpile

import neqr
import random
import steganography
'''
NEQR Unit Tests
'''
def convert_to_bits_test(): 
    array2x2 = [[random.randint(0, 255), random.randint(0, 255)], [random.randint(0, 255), random.randint(0, 255)]]
    print(array2x2)
    bits_arr = neqr.convert_to_bits(array2x2)
    print(bits_arr)

def neqr_test():
    array2x2 = [[random.randint(0, 255), random.randint(0, 255)], [random.randint(0, 255), random.randint(0, 255)]]
    print('2x2 array:')
    print(array2x2)
    print(neqr.convert_to_bits(array2x2))

    flattened_array = neqr.convert_to_bits(array2x2)
    result_circuit = neqr.neqr(flattened_array)

    backend = Aer.get_backend('statevector_simulator')
    job = execute(result_circuit, backend=backend, shots=1, memory=True)
    job_result = job.result()
    statevec = job_result.get_statevector(result_circuit)
    for i in range(len(statevec)):
        if statevec[i] != 0:
            print(f"{format(i, '010b')}: {statevec[i].real}")

############################################################################################################################

'''
Steganography Unit Tests
'''
def comparator_test():
    #creating registers and adding them to circuit 
    regX = QuantumRegister(4, "Register X")
    regY = QuantumRegister(4, "Register Y")
    circuit = QuantumCircuit(regX, regY)

    #changing registers to make them different 
    circuit.x(regX[1])
    circuit.x(regX[3])
    circuit.x(regY[0])
    circuit.x(regY[2])
    
    #comparator returns the circuit
    resultCircuit = steganography.comparator(regY, regX, circuit)
    #result --> ancillas from function
    resultCircuit.measure(result)

    #measuring
    backend = Aer.get_backend('statevector_simulator')
    simulation = execute(resultCircuit, backend=backend, shots=1, memory=True)
    simResult = simulation.result()
    statevec = simResult.get_statevector(resultCircuit)
    for state in range(len(statevec)):
        print(f"{format(state, '010b')}: {statevec[state].real}")

    


def coordinate_comparator_test():
<<<<<<< HEAD
    regXY = QuantumRegister(2, "reg1")
    regAB = QuantumRegister(2, "reg2")
    circuit = QuantumCircuit(regXY, regAB)
    #uncomment this to make the registers different
    #regXY is in |00> and regAB in |01>
    #circuit.x(regAB[1])
    #circuit.x(regXY[1])
    resultCircuit = steganography.coordinate_comparator(circuit, regXY, regAB)
    print(resultCircuit.draw())
    backend = Aer.get_backend('statevector_simulator')
    simulation = execute(resultCircuit, backend=backend, shots=1, memory=True)
    simResult = simulation.result()
    statevec = simResult.get_statevector(resultCircuit)
    for state in range(len(statevec)):
        if statevec[state] != 0:
            #note: output is in little endian
            print(f"{format(state, '05b')}: {statevec[state].real}")
=======
    pass

def difference_test():
    pass
>>>>>>> b003b6b776bd5a7f33fac926288f51bf402c6236


<<<<<<< HEAD


def main():
    coordinate_comparator_test()
=======
def main():
    comparator_test()
>>>>>>> b003b6b776bd5a7f33fac926288f51bf402c6236

if __name__ == '__main__':
    main()