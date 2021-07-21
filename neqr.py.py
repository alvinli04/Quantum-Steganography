import qiskit

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




if __name__ == '__main__':
    print('hello')
