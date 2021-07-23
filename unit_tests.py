from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, AncillaRegister
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
    resultCircuit, _ = steganography.comparator(regY, regX, circuit, result)
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


def get_secret_image_test():
    test_arr = [[[random.randint(0,1) for i in range(4)] for j in range(4)] for k in range(5)]
    test_result = steganography.get_secret_image(5, test_arr)
    for a in test_arr:
        print(a)
    print(f'result:\n {test_result}')


def invert_test():
    test_arr = arraynxn(4)
    print(neqr.convert_to_bits(test_arr))
    test_circuit, intensity = neqr.neqr(neqr.convert_to_bits(test_arr))
    steganography.invert(test_circuit, intensity)

    backend = Aer.get_backend('statevector_simulator')
    simulation = execute(test_circuit, backend=backend, shots=1, memory=True)
    simResult = simulation.result()
    statevec = simResult.get_statevector(test_circuit)
    for state in range(len(statevec)):
        if statevec[state] != 0:
            #note: output is in little endian
            #only have to look at first bit 
            print(f"{format(state, '012b')}: {statevec[state].real}")


def get_key_test():
    test_cover = arraynxn(2)
    test_secret = arraynxn(2)
    print(f'cover:\n {test_cover} \n secret:\n {test_secret}')
    sz = 4
    (cover, cover_intensity, cover_idx) = neqr.neqr(test_cover)
    (secret, secret_intensity, secret_idx) = neqr.neqr(test_secret)

    key_idx, key_result = QuantumRegister(len(secret_idx)), QuantumRegister(1)
    inv = QuantumRegister(len(secret_intensity))
    diff1 = QuantumRegister(len(secret_intensity))
    diff2 = QuantumRegister(len(secret_intensity))

    print(len(cover_idx), len(secret_idx), len(key_idx))

    circuit = QuantumCircuit(cover_intensity, cover_idx, secret_intensity, secret_idx, key_idx, key_result, inv, diff1, diff2)

    steganography.invert(circuit, secret_intensity, inv)

    steganography.get_key(circuit, key_idx, key_result, cover_idx, cover_intensity, secret_idx, secret_intensity, inv, diff1, diff2, sz)

    backend = Aer.get_backend('statevector_simulator')
    simulation = execute(circuit, backend=backend, shots=1, memory=True)
    simResult = simulation.result()
    statevec = simResult.get_statevector(circuit)
    for state in range(len(statevec)):
        if statevec[state] != 0:
            #note: output is in little endian
            #only have to look at first bit 
            print(f"{format(state, '012b')}: {statevec[state].real}")


def main():
    get_key_test()
    #print("\n Comparator Test: ", comparator_test(), "\n")
    #coordinate_comparator_test()

if __name__ == '__main__':
    main()