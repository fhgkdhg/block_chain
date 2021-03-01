#!/bin/usr/python3

import ecdsa
import hashlib
import base58
import binascii
import json

class Wallets:
    def __init__(self):
        self.__wallet = []
        walletfile = open('wallet.json','r')
        data = walletfile.read()
        if not(len(data) == 0):
            self.__wallet = json.loads(data)
            

    def new_key_pair(self):
        # 生成公私钥对
        private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        public_key = private_key.get_verifying_key().to_string().hex()
        
        # 生成地址,首先运用ripemd160(sha256())算法对公钥进行处理
        hash_pub_key = hashlib.sha256(binascii.unhexlify(public_key)).hexdigest()
        ripemd160 = hashlib.new('ripemd160',binascii.unhexlify(hash_pub_key))

        # 加上网络版本号'00',并进行两次哈希
        prepend_network_byte = '00' + ripemd160.hexdigest()
        # print('prepend_network_byte: ' + prepend_network_byte)

        hash = prepend_network_byte
        for i in range(1,3):
            hash = hashlib.sha256(binascii.unhexlify(hash)).hexdigest()
        
        # 取前4字节作为校验和
        check_sum = hash[:8]
        # print('check_sum: ' + check_sum)

        # 拼接并进行base58编码生成比特币地址
        bitcoin_address = prepend_network_byte + check_sum
        # print('bitcion_address: ' + bitcoin_address)

        address = base58.b58encode(bytes.fromhex(bitcoin_address))

        print("new address: " + address.decode('utf8'))

        # 将生成的公私钥对写入文件
        self.__wallet.append({'private_key':private_key.to_string().hex(),'public_key':public_key,'address':address.decode('utf8')})
        walletfile = open('wallet.json','w')
        walletfile.write(json.dumps(self.__wallet))
        walletfile.close()

    def print_key(self):
        if len(self.__wallet) == 0:
            print('Empty!')
        else:
            for wallet in self.__wallet:
                print('private_key: ' + str(wallet['private_key']))
                print('public_key: ' + str(wallet['public_key']))
                print('address: ' + wallet['address'])

    def print_address(self):
        if len(self.__wallet)==0:
            print('Empty!')
        else:
            for i in range(len(self.__wallet)):
                print('address ' + str(i+1) + ': ' + self.__wallet[i]['address'])
        
    def get_genesis_pub_key(self):
        return self.__wallet[0]['public_key']

    def get_wallets(self):
        return self.__wallet