#!/usr/bin/python3

import sys
from wallet import Wallets
from block_chain import Block_chain



def create_block_chain():
    bc = Block_chain()
    bc.print_chain()

def get_balance(address):
    bc = Block_chain()
    balance = bc.get_balance(address)
    print('balance of ' + address + ': ' + str(balance))    


def send(s_address,d_address,amount):
    bc = Block_chain()
    bc.send(s_address,d_address,amount)


def print_chain():
    bc = Block_chain()
    bc.print_chain()


def print_address():
    wallet = Wallets()
    wallet.print_address()

def print_key():
    wallet = Wallets()
    wallet.print_key()

def create_wallet():
    wallet = Wallets()
    wallet.new_key_pair()


def exec(argc,argv):
    if argc < 2:
        print("Wrong command!")
        # ./main.py create_wallet
    elif argc == 2:
        if argv[1] == 'create_wallet':
            create_wallet()
            # ./main.py print_address
        elif argv[1] == 'print_address':
            print_address()
            # ./main.py print_key
        elif argv[1] == 'print_key':
            print_key()
            # ./main.py create_block_chain
        elif argv[1] == 'create_block_chain':
            create_block_chain()
            # ./main.py print_chain
        elif argv[1] == 'print_chain':
            print_chain()
        else:
            print('Wrong command!')
        # ./main.py get_balance -address address
    elif argc == 4:
        if argv[1] == 'get_balance' and argv[2] == '-address':
            get_balance(argv[3])
        else:
            print("Wrong command!")
        # ./main.py send -from s_address -to d_address -amount amount
    elif argc==8 and argv[1]=='send' and argv[2]=='-from' and argv[4]=='-to' and argv[6]=='-amount':
        send(argv[3],argv[5],float(argv[7]))
    else:
        print('Wrong command!')
