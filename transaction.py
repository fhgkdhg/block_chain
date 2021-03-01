from hashlib import sha256
from txinput import TxInput
from txoutput import TxOutput
import ecdsa
import binascii
import pickle
import block_chain

class Transaction():
    def __init__(self,Vin,Vout):
        self.__vin = Vin
        self.__vout = Vout

        # 将交易的输入与输出数据连接起来,生成交易ID
        data = ''.encode('utf8')
        for vi in self.__vin:
            data += vi.serialize()
        for vo in self.__vout:
            data += vo.serialize()
        self.__id = sha256(data).hexdigest()
    
    def get_id(self):
        return self.__id

    def get_vout(self):
        return self.__vout

    def get_vin(self):
        return self.__vin

    def sign(self,priv_key):
        data = ''
        # 本交易的输入方的序列化数据,不包括输入方的签名和输出方的公钥哈希
        for vin in self.__vin:
            data += str(vin.get_tx_id()) + str(vin.get_index())
        for vout in self.__vout:
            data += str(vout.get_value())
        
        serial_data = pickle.dumps(data.encode('utf8'))
        for vin in self.__vin:
            # 对私钥进行格式转换,并对本笔交易进行签名
            private_key = ecdsa.SigningKey.from_string(bytes.fromhex(priv_key),curve=ecdsa.SECP256k1)
            vin.set_signature(private_key.sign(serial_data))

    def verify(self,pub_key):
        bc = block_chain.Block_chain()
        
        # 获取本笔交易序列化数据
        data = ''
        for vin in self.__vin:
            data += str(vin.get_tx_id()) + str(vin.get_index())
        for vout in self.__vout:
            data += str(vout.get_value())

        serial_data = pickle.dumps(data.encode('utf8'))

        for vin in self.__vin:
            # 对于每笔交易,首先验证引用的输出是自己可用的
            pre_tran = bc.find_transaction(vin.get_tx_id())
            
            # 引用的交易不存在,返回错误
            if pre_tran == None:
                print('Transaction error!')
                return False
            pre_vout = pre_tran.get_vout()

            # 上笔交易不可用,返回错误
            if not(pre_vout[vin.get_index()].get_pub_key_hash() == sha256(vin.get_pub_key()).hexdigest()):
                print(pre_vout[vin.get_index()].get_pub_key_hash())
                print(sha256(vin.get_pub_key()).hexdigest())
                print('you are unbale to use the transaction!')
                return False
            
            # 本笔交易签名验证错误,返回错误
            public_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(vin.get_pub_key().decode('utf8')),curve=ecdsa.SECP256k1)
            if not(public_key.verify(vin.get_signature(),serial_data)):
                print('signature error!')
                return False
        return True
            