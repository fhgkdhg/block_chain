#!/usr/bin/python3

from block import Block
from pickle import loads
from pickle import dumps
import boltdb
from transaction import Transaction
from txinput import TxInput
from txoutput import TxOutput
from wallet import Wallets
from binascii import unhexlify
from hashlib import sha256

class Block_chain:
    def __init__(self):
        
        # print('blockchain init...')
        # 打开临时数据库文件
        self.__db = boltdb.BoltDB("bolt.db")
        with self.__db.update() as bolt:
            bucket = bolt.bucket(b'blocks')
            # 生成创世区块
            # tip存储链中最后一个区块的哈希
            if bucket == None:
                wallets = Wallets()
                self.__tip = self.genesis_block(wallets.get_genesis_pub_key(),bolt)
            else:
                self.__tip = loads(bucket.get(b'tip'))



    def add_block(self,transactions):
        # print('block generating...')
        new_block = Block(self.__tip,transactions)
        self.__tip = new_block.get_hash()
        
        with self.__db.update() as bolt:
            hash = dumps(self.__tip)
            serial_block = dumps(new_block)
            bolt.bucket(b'blocks').put(hash,serial_block)
            
            # 新区块放入, 更改tip
            bolt.bucket(b'blocks').delete(b'tip') 
            bolt.bucket(b'blocks').put(b'tip',hash)

    def send(self,s_address,d_address,amount):
        # 定义Vin与Vout,生成新交易并放入区块中,多余的钱返回自己账户
        vin = []
        vout = []
        spendable_txout = self.get_spendable_txout(s_address)

        wlt = Wallets()
        wallets = wlt.get_wallets()
        s_pub_key = ''
        d_pub_key = ''
        for wallet in wallets:
            if wallet['address'] == s_address:
                s_priv_key = wallet['private_key']
                s_pub_key = wallet['public_key']
            if wallet['address'] == d_address:
                d_pub_key = wallet['public_key']
        if len(s_pub_key) ==0 or len(d_pub_key) ==0 :
            print("Wrong address!")
        else:
            d_pub_key_hash = sha256(d_pub_key.encode('utf8')).hexdigest()
            s_pub_key_hash = sha256(s_pub_key.encode('utf8')).hexdigest()
            # 生成交易的输入和输出list
            spendable_amount = 0
            for txout in spendable_txout:
                spendable_amount += txout['value']
                tempin = TxInput(txout['tran_id'],txout['index'],s_pub_key.encode('utf8'))
                vin.append(tempin)
                if spendable_amount > amount:
                    break
            
            if spendable_amount > amount:
                # 转出amount,剩余转回给自己
                remain = spendable_amount - amount
                vout.append(TxOutput(amount,d_pub_key_hash))
                vout.append(TxOutput(remain,s_pub_key_hash))
                trans = []
                trans.append(Transaction(vin,vout))
                
                # 对交易签名
                for tran in trans:
                    tran.sign(s_priv_key)

                # 矿工的工作,对交易进行验证,验证通过后打包进区块
                for tran in trans:
                    if not(tran.verify(s_pub_key)):
                        print('Failed!')
                        return
                
                # 将交易打包入区块中
                self.add_block(trans)     
                print("Success!")    
            elif spendable_amount == amount:
                vout.append(TxOutput(amount,d_address))
                trans = []
                trans.append(Transaction(vin,vout))

                # 对交易签名
                for tran in trans:
                    tran.sign(s_priv_key)

                # 矿工的工作,对交易进行验证,验证通过后打包进区块
                for tran in trans:
                    if not(tran.verify(s_pub_key)):
                        print('Failed!')
                        return
                    
                
                # 将交易打包入区块中
                self.add_block(trans)
                print("Success!")
            elif spendable_amount < amount:
                print('Insufficient balance!')
            
        
    
    def genesis_block(self,genesis_pub_key,bolt):
        # 创世区块的交易,新块奖励金
        vin = []
        vout = []
        data = 'Reward'
        pub_key_hash = sha256(genesis_pub_key.encode('utf8')).hexdigest()
        vin.append(TxInput('',-1,data))
        vout.append(TxOutput(10,pub_key_hash))
        trans = []
        trans.append(Transaction(vin,vout))

        # 生成新区块,并将交易打包进区块
        new_block = Block('',trans)
        # self.__blocks.append(new_block)
        
        # 将创世区块放入数据库中
        # 创建bucket
        bucket = bolt.create_bucket(b'blocks')
        
        # 序列化哈希与区块
        hash = dumps(new_block.get_hash())
        serial_block = dumps(new_block)
        
        # 将区块与对应哈希放入数据库
        # 将最后的区块hash放入数据库
        bucket.put(hash,serial_block)
        bucket.put(b'tip',hash)
        return new_block.get_hash()

    def print_chain(self):
        # 打开临时数据库文件
        with self.__db.view() as bolt:
            bucket = bolt.bucket(b'blocks')
            pre_hash = bucket.get(b'tip')
            while(loads(pre_hash)):
                current_block = loads(bucket.get(pre_hash))
                current_block.show_block_info()
                pre_hash = dumps(current_block.get_pre_block_hash())


    def get_balance(self,address):
        # balance: 余额
        # tx_output: 链中所有关于address的输出
        # blocks: 用于存放待检查区块
        balance = 0
        blocks = []
        
        # 接入数据库
        with self.__db.view() as bolt:
            bucket = bolt.bucket(b'blocks')
            pre_hash = bucket.get(b'tip')
            while(loads(pre_hash)):
                # 区块链从后往前遍历,直到创世区块
                current_block = loads(bucket.get(pre_hash))
                
                # 检查current_block中关于address的交易的输出
                # 是否在blocks中的交易的输入里
                trans = current_block.get_transactions()
                for tran in trans:
                    tran_id = tran.get_id()
                    vout = tran.get_vout()
                    for i in range(len(vout)):
                        # 找到与address关联的输出
                        # 当前输出的参数为:
                        # id: tran_id
                        # index: i

                        # flag: 是否存在的标志
                        flag = False
                        # 检查其是否在blocks的交易的输入里
                        # 是则跳过,否则统计余额
                        if vout[i].can_be_unlock(address):
                            for blk in blocks:
                                inter_trans = blk.get_transactions()
                                for inter_tran in inter_trans:
                                    inter_vin = inter_tran.get_vin()
                                    for inp in inter_vin:
                                        if inp.get_tx_id() == tran_id and inp.get_index() == i:
                                            flag = True
                            if flag == False:
                                balance += vout[i].get_value()
                
                blocks.append(current_block)
                pre_hash = dumps(current_block.get_pre_block_hash())
        
        return balance

    def get_spendable_txout(self,address):
        # 存放着可用花费
        result = []
        blocks = []
        
        # 接入数据库
        with self.__db.view() as bolt:
            bucket = bolt.bucket(b'blocks')
            pre_hash = bucket.get(b'tip')
            while(loads(pre_hash)):
                # 区块链从后往前遍历,直到创世区块
                current_block = loads(bucket.get(pre_hash))
                
                # 检查current_block中关于address的交易的输出
                # 是否在blocks中的交易的输入里
                trans = current_block.get_transactions()
                for tran in trans:
                    tran_id = tran.get_id()
                    vout = tran.get_vout()
                    for i in range(len(vout)):
                        # 找到与address关联的输出
                        # 当前输出的参数为:
                        # id: tran_id
                        # index: i

                        # flag: 是否存在的标志
                        flag = False
                        if vout[i].can_be_unlock(address):
                            # 检查其是否在blocks的交易的输入里
                            # 是则跳过,否则统计余额
                            for blk in blocks:
                                inter_trans = blk.get_transactions()
                                for inter_tran in inter_trans:
                                    inter_vin = inter_tran.get_vin()
                                    for inp in inter_vin:
                                        if inp.get_tx_id() == tran_id and inp.get_index() == i and inp.can_be_unlock(address):
                                            flag =True
                            if flag==False:
                              result.append({'tran_id':tran_id,'index':i,'value':vout[i].get_value()})
                
                blocks.append(current_block)
                pre_hash = dumps(current_block.get_pre_block_hash())
        
        return result

    def find_transaction(self,tran_id):
        with self.__db.view() as bolt:
            bucket = bolt.bucket(b'blocks')
            pre_hash = bucket.get(b'tip')
            while(loads(pre_hash)):
                # 区块链从后往前遍历,直到创世区块
                current_block = loads(bucket.get(pre_hash))
                for tran in current_block.get_transactions():
                    if tran.get_id() == tran_id:
                        return tran
                pre_hash = dumps(current_block.get_pre_block_hash())
            return None