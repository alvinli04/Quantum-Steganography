from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import Aer
from qiskit import IBMQ
from qiskit.compiler import transpile

import neqr
import random
import steganography


def arraynxn(n):
    return [[random.randint(0,255) for i in range(n)] for j in range(n)]

'''
NEQR Unit Tests
'''
def convert_to_bits_test(): 
    array2x2 = [[random.randint(0, 255), random.randint(0, 255)], [random.randint(0, 255), random.randint(0, 255)]]
    print(array2x2)
    bits_arr = neqr.convert_to_bits(array2x2)
    print(bits_arr)

def neqr_test():
    testarr = arraynxn(4)
    print('test array:')
    print(testarr)

    flattened_array = neqr.convert_to_bits(testarr)

    print([''.join([str(b) for i,b in enumerate(a)]) for a in flattened_array])

    result_circuit = neqr.neqr(flattened_array)

    backend = Aer.get_backend('statevector_simulator')
    job = execute(result_circuit, backend=backend, shots=1, memory=True)
    job_result = job.result()
    statevec = job_result.get_statevector(result_circuit)
    for i in range(len(statevec)):
        if statevec[i] != 0:
            print(f"{format(i, '012b')}: {statevec[i].real}")
    print(result_circuit)

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

def difference_test():
    regY = QuantumRegister(4, "regY")
    regX = QuantumRegister(4, "regX")
    difference = QuantumRegister(4, 'difference')
    cr = ClassicalRegister(4, 'measurement')
    circuit = QuantumCircuit(regY, regX, difference, cr)
    
    circuit.barrier()

    steganography.difference(circuit, regY, regX, difference)
    #print(circuit.draw())

    circuit.measure(difference, cr)

    simulator = Aer.get_backend('aer_simulator')
    simulation = execute(circuit, simulator, shots=1)
    result = simulation.result()
    counts = result.get_counts(circuit)

    for(state, count) in counts.items():
        big_endian_state = state[::-1]
        print(big_endian_state)


def main():
    difference_test()

if __name__ == '__main__':
    main()