#!/usr/bin/python3

import wallet
import hashlib

class TxOutput():
    def __init__(self,value,pub_key_hash):
        self.__value = value
        self.__pub_key_hash = pub_key_hash


    def get_value(self):
        return self.__value


    def get_pub_key_hash(self):
        return self.__pub_key_hash

    def serialize(self):
        data = str(self.__value) + str(self.__pub_key_hash)
        return data.encode('utf8')

    def can_be_unlock(self,address):
        # 找到address对应的公钥
        pub_key = ''
        wallets = wallet.Wallets()
        for wlt in wallets.get_wallets():
            if wlt['address'] == address:
                pub_key = wlt['public_key']
        hash = hashlib.sha256(pub_key.encode('utf8')).hexdigest()
        return self.__pub_key_hash == hash