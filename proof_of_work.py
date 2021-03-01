#!/usr/bin/python3

from hashlib import sha256

class Proof_of_work:
    def __init__(self,block):

        # 挖矿难度,哈希值前n位为0
        self.__target_bits =24
        self.target = int(1 << (256-self.__target_bits))
        
        # 获取区块基础数据
        self.__transactions = block.get_transactions()
        self.__pre_block_hash = block.get_pre_block_hash()
        self.__time_stamp = block.get_time_stamp()
        
    
    # 计算满足条件的Hash值,并返回 nonce, hash
    def run(self):
        print("Mining the block containing...")
        
        # serialize trans
        trans = ''
        for tx in self.__transactions:
            trans += tx.get_id()
        data = self.__pre_block_hash + trans + self.__time_stamp
        
        for nonce in range(2**64):
            hash = sha256((data+str(nonce)).encode('utf8')).hexdigest()
            if int(hash,16) < self.target:
                print('found! ' + hash)
                return {'hash':hash,'nonce':nonce}


    # 对工作量证明的验证
    def validate(self,block):
        data = str(block.get_pre_block_hash()) + block.get_data() + block.get_time_stamp()
        data += str(block.get_nonce())
        hash = sha256(data.encode('utf8')).hexdigest()
        if int(hash,16) < self.target:
            return True
        else:
            return False