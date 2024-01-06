#!/usr/bin/env python3

from bitarray import bitarray


# Constants 

L = 6
WORD = 64
WIDTH = 1600


# Padding

# if parity is already achieved,
# we add rate bits (total block)
#
# if we only have to add 1 bit to achieve parity,
# we add 1+rate bits (1 bit to the last block, and a total block)
#
# if we only have to add n (1 < n < rate) bit to achieve parity,
# we add n bits to the last block
def pad(msg: bitarray, rate: int):
    zeroes = (rate - 2 - (len(msg) % rate)) % rate
    remainder = bitarray('1') + zeroes * bitarray('0') + bitarray('1')

    msg += remainder



# Permutations utils

def get_3d_bit(s: bitarray, x: int, y: int, z: int) -> bool:
    assert(x < 5 and y < 5 and z < WORD)
    return s[WORD * (5 * y + x) + z]

def set_3d_bit(s: bitarray, x: int, y: int, z: int, newval: bool):
    assert(x < 5 and y < 5 and z < WORD)
    s[WORD * (5 * y + x) + z] = newval



# Permutations

def theta(a: bitarray) -> bitarray:
    def c(x: int, z: int) -> bool:
        return get_3d_bit(a, x, 0, z) ^ get_3d_bit(a, x, 1, z) ^ get_3d_bit(a, x, 2, z) ^ get_3d_bit(a, x, 3, z) ^ get_3d_bit(a, x, 4, z)

    def d(x: int , z: int) -> bool:
        return c((x - 1) % 5, z) ^ c((x + 1) % 5, (z - 1) % WORD)

    a_new = bitarray('0', endian = 'little') * WIDTH

    for x in range(5):
        for y in range(5):
            for z in range(WORD):
                tmp = get_3d_bit(a, x, y, z) ^ d(x, z)
                set_3d_bit(a_new, x, y, z, tmp)
    
    return a_new


def rho(a: bitarray) -> bitarray:
    a_new = bitarray('0', endian = 'little') * WIDTH

    for z in range(WORD):
        tmp = get_3d_bit(a, 0, 0, z)
        set_3d_bit(a_new, 0, 0, z, tmp)

    (x, y) = (1, 0)

    for t in range(24):
        for z in range(WORD):
            tmp = get_3d_bit(a, x, y, (z - ((t + 1) * (t + 2)) // 2) % WORD)
            set_3d_bit(a_new, x, y, z, tmp)
        
        (x, y) = (y, (2 * x + 3 * y) % 5)

    return a_new

def pi(a: bitarray) -> bitarray:
    a_new = bitarray('0', endian = 'little') * WIDTH

    for x in range(5):
        for y in range(5):
            for z in range(WORD):
                tmp = get_3d_bit(a, (x + 3 * y) % 5, x, z)
                set_3d_bit(a_new, x, y, z, tmp)

    return a_new

def chi(a: bitarray) -> bitarray:
    a_new = bitarray('0', endian = 'little') * WIDTH

    for x in range(5):
        for y in range(5):
            for z in range(WORD):
                tmp = get_3d_bit(a, x, y, z) ^ ((get_3d_bit(a, (x + 1) % 5, y, z) ^ 1) * get_3d_bit(a, (x + 2) % 5, y, z))

                set_3d_bit(a_new, x, y, z, tmp)

    return a_new

def iota(a: bitarray, ir: int) -> bitarray:
    def rc(t: int) -> bool:
        if t % 255 == 0:
            return 1

        r = bitarray('10000000', endian='little') 

        for i in range(t % 255):
            eightBit = r[7]
            r >>= 1

            r[0] ^= eightBit
            r[4] ^= eightBit
            r[5] ^= eightBit
            r[6] ^= eightBit

        return r[0]

    RC = bitarray('0', endian = 'little') * WORD

    for y in range(L + 1):
        RC[2 ** y - 1] = rc(y + 7 * ir) # normally calculated at compile time

    a_new = a
        
    for z in range(WORD):
        tmp = get_3d_bit(a_new, 0, 0, z) ^ RC[z]
        set_3d_bit(a_new, 0, 0, z, tmp)

    return a_new


    
def f(state: bitarray) -> bitarray:
    for ir in range(12 + 2 * L):
        state = iota(chi(pi(rho(theta(state)))), ir)

    return state



def absorb(msg: bitarray, rate: int, capacity: int) -> bitarray:
    state = bitarray('0', endian='little') * WIDTH

    for x in range(len(msg) // rate):
        state[0 : rate] ^= msg[x * rate : (x + 1) * rate]
        state = f(state)

    return state

def squish(state: bitarray, rate: int, digest: int) -> bitarray:
    z = bitarray(endian = 'little')

    while digest > len(z):
        z += state[0 : rate]
        state = f(state)

    return z[0 : digest]

# Main function

def sha3(data: bytes, rate: int, capacity: int) -> bytes:
    assert(rate + capacity == WIDTH) 

    msg = bitarray(endian='little')
    msg.frombytes(data)
    msg += bitarray('01', endian='little')

    pad(msg, rate)
    state = absorb(msg, rate, capacity)
    return squish(state, rate, capacity // 2).tobytes()


# Wrappers

def sha3_512(data):
    return sha3(data, 576, 1024)

def sha3_384(data):
    return sha3(data, 832, 768)

def sha3_256(data):
    return sha3(data, 1088, 512)

def sha3_224(data):
    return sha3(data, 1152, 448)

def main():
    # print(bytes(sha3_224(bytes("The quick brown fox jumps over the lazy dog", encoding="utf-8"))).hex())
    # print(bytes(sha3_224(bytes("The quick brown fox jumps over the lazy dog.", encoding="utf-8"))).hex())

    # print(bytes(sha3_512(bytes("The quick brown fox jumps over the lazy dog", encoding="utf-8"))).hex())
    # print(bytes(sha3_512(bytes("The quick brown fox jumps over the lazy dog.", encoding="utf-8"))).hex())

    with open("smallfile", "rb") as f: # head -c 1K </dev/urandom> smallfile
        data = f.read()
        print("sha3_256, smallfile: ", sha3_256(data).hex())

    with open("largefile", "rb") as f: # head -c 1M </dev/urandom> largefile
        data = f.read()
        print("sha3_512, largefile: ", sha3_512(data).hex())


if __name__ == '__main__':
    main()
