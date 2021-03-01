#!/usr/bin/python3

import time
from hashlib import sha256
from proof_of_work import Proof_of_work
from transaction import Transaction

class Block(object):
    def __init__(self,pre_block_hash,transactions):
        
        # 基础数据
        self.__pre_block_hash = pre_block_hash
        self.__time_stamp = str(time.time()*1000)
        self.__transactions = transactions
        
        # 工作量证明
        pow = Proof_of_work(self)
        res = pow.run()
        
        #Hash 以及 Nonce
        self.__hash = res['hash']
        self.__nonce = res['nonce']
        

    # 已用 proof_of_work 代替

    # def set_hash(self,pre_block_hash,data):
    #     headers = str(pre_block_hash) + data 
    #     headers += self.__time_stamp
    #     return sha256(headers.encode('utf-8')).hexdigest()


    def show_block_info(self):
        print('###########################################')
        print("hash".ljust(15,' ') + ' : ' + str(self.__hash))
        print("pre_block_hash".ljust(15,' ') + ' : ' + str(self.__pre_block_hash))
        print("trans:")
        for tran in self.__transactions:
            print("********************************************")
            print('TX_id:' + str(tran.get_id()))
            print("    input:")
            for input in tran.get_vin():
                print("        tx_id:" + str(input.get_tx_id()))
                print("        index:" + str(input.get_index()))
                print("        signature:" + str(input.get_signature()))
                print("        ---------------------------------------")
            print("    output:")
            for output in tran.get_vout():
                print("        value:" + str(output.get_value()))
                print("        pub_key_hash:" + str(output.get_pub_key_hash()))
                print("        ---------------------------------------")
            print("********************************************")
        # print('nonce'.ljust(15,' ') + str(self.__nonce))
        # print("time_stamp".ljust(15,' ') + ' : ' + self.__time_stamp)
        print('###########################################')


    def get_hash(self):
        return self.__hash

    def get_transactions(self):
        return self.__transactions

    def get_pre_block_hash(self):
        return self.__pre_block_hash

    def get_time_stamp(self):
        return self.__time_stamp

    def get_nonce(self):
        return self.__nonce

    def is_genesis_block(self):
        index = self.__transactions[0].get_vin[0].get_index()
        if index == -1:
            return True
        else:
            return False
    