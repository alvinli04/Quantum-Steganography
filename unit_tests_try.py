from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute
from qiskit import Aer
from qiskit import IBMQ
from qiskit.compiler import transpile

import neqr
import random
import steganography

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

def comparator_test():
    #creating registers and adding them to circuit 
    regX = QuantumRegister(4)
    regY = QuantumRegister(4)
    circuit = QuantumCircuit(regX, regY)
    cr = ClassicalRegister(2)

    #changing registers to make them different 
    circuit.x(regX[0])
    circuit.x(regX[2])
    circuit.x(regY[1])
    circuit.x(regY[3])

    result = QuantumRegister(2, 'result')
    circuit.add_register(result)

    circuit.add_register(cr)
    
    #comparator returns the circuit
    resultCircuit = steganography.comparator(regY, regX, circuit, result)
    #result --> ancillas from function
    resultCircuit.measure(result, cr)

    #measuring
    simulator = Aer.get_backend('aer_simulator')
    simulation = execute(resultCircuit, simulator, shots=1, memory=True)
    simResult = simulation.result()
    counts = simResult.get_counts(resultCircuit)
    for(state, count) in counts.items():
        big_endian_state = state[::-1]
        return big_endian_state

def main():
    convert_to_bits_test()
    neqr_test()
    print(comparator_test())

if __name__ == '__main__':
    main()