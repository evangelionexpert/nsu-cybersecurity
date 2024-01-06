#!/usr/bin/env python3
from smolyakov_rsa import *

def main():
    keylen = 1024
    pub_key, priv_key = rsa_gen_keys(keylen)

    print('using ', keylen, ' bit keys')
    print('pubkey: ', pub_key)
    print('privkey: ', priv_key)

    print()
    print('*** ENCRYPTION TEST ***')
 
    msg = b'hello, this is encryption test'
    print('original msg: ', msg)

    cipher = rsa_encrypt(msg, pub_key)
    print('cipher:', hex(cipher))

    decr = rsa_decrypt(cipher, priv_key)
    print('decrypted (with padding removed): ', decr[:len(msg)])



    print()
    print('*** SIMPLE SIGNATURE TEST ***')

    msg = b'hello, this is signature'
    print('original msg: ', msg)

    sign = rsa_signature_gen(msg, priv_key)
    print('sign cipher: ', hex(sign))

    msg_from_sign, verified = rsa_signature_verify(msg, sign, pub_key)
    print('msg from sign: ', msg_from_sign)
    print('verified: ', verified)



    print()
    print('*** SHA3-512 SIGNATURE TEST ***')
    print('~ signing')
    with open("largefile-sign", "rb") as f: # head -c 64K </dev/urandom> largefile
        msg = f.read()
        sign_hash, sign = rsa_signature_gen_sha3_512(msg, priv_key)
        print('sign hash: ', sign_hash)

    print()
    print('~ true')
    with open("largefile-verify", "rb") as f: # head -c 64K </dev/urandom> largefile
        msg = f.read()
        decrypted_hash, true_hash, verified = rsa_signature_verify_sha3_512(msg, sign, pub_key)
        print('decrypted hash: ', decrypted_hash)
        print('true hash: ', true_hash)
        print('verified: ', verified)

    print()
    print('~ fake')
    with open("largefile-fake", "rb") as f: # head -c 64K </dev/urandom> largefile
        msg = f.read()
        decrypted_hash, true_hash, verified = rsa_signature_verify_sha3_512(msg, sign, pub_key)
        print('decrypted hash: ', decrypted_hash)
        print('true hash: ', true_hash)
        print('verified: ', verified)

    print()


if __name__ == '__main__':
    main()
