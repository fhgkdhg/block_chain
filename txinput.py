#!/usr/bin/python3

class TxInput:
    def __init__(self,tx_id,vout,pub_key):
        # tx_id:上笔输出交易的ID 
        # index:交易中输出的索引
        # script_sig:解锁的数据
        # pub_key_hash:发起交易人的公钥哈希
        self.__tx_id = tx_id
        self.__vout = vout
        self.__signature = b''
        self.__pub_key = pub_key
    

    def get_index(self):
        return self.__vout

    def get_tx_id(self):
        return self.__tx_id


    def get_signature(self):
        return self.__signature

    def serialize(self):
        data = str(self.__tx_id) + str(self.__vout) + str(self.__signature)
        return data.encode('utf8')

    def set_signature(self,signature):
        self.__signature = signature

    def get_pub_key(self):
        return self.__pub_key

    def can_be_unlock(self,address):
        return self.__signature == address