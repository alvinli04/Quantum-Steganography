import neqr
import qiskit
import random

def test1(): 
    array = [[random.randint(0, 255), random.randint(0, 255)], [random.randint(0, 255), random.randint(0, 255)]]
    print(array)
    bits_arr = neqr.convert_to_bits(array)
    print(bits_arr)
    
test1()