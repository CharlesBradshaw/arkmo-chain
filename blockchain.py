import hashlib as hasher
import json
from datetime import datetime
from random import randint

import arky.rest


class Block:
    def __init__(self, data, previous_hash):
        self.data = data
        data['timestamp'] = str(datetime.now())
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        sha = hasher.sha256()
        sha.update((json.dumps(self.data) + str(self.previous_hash)).encode('utf-8'))
        return sha.hexdigest()


class Blockchain:

    def __init__(self):
        self.unaccepted_payments = set()
        self.finalized_payments = {}
        self.chain = []
        self.block_hash_dict = {}
        self.address_public_key_dict = {}
        self.address_username_dict = {}
        self.address_transactions_dict = {}
        self.create_genesis_block()
        arky.rest.use("dark")

    def create_genesis_block(self):
        data = {}
        new_block = Block(data, 0)
        self.chain.append(new_block)
        self.block_hash_dict[new_block.hash] = new_block
        return new_block

    def create_generic_block(self, data):

        new_block = Block(data, self.chain[-1].hash)
        self.chain.append(new_block)
        self.block_hash_dict[new_block.hash] = new_block
        return new_block

    def add_create_block(self, block, source_address, target_address):
        self.unaccepted_payments.add(block.hash)

        if source_address not in self.address_transactions_dict:
            self.address_transactions_dict[source_address] = {}
        if target_address not in self.address_transactions_dict:
            self.address_transactions_dict[target_address] = {}

        self.address_transactions_dict[source_address][block.hash] = {"block": block.__dict__,
                                                                      'status': 'pending',
                                                                      'source_username': self.get_username(
                                                                          source_address),
                                                                      'target_username': self.get_username(
                                                                          target_address)}
        self.address_transactions_dict[target_address][block.hash] = {"block": block.__dict__, 'status': 'pending',
                                                                      'source_username': self.get_username(
                                                                          source_address),
                                                                      'target_username': self.get_username(
                                                                          target_address)}

    def create_request_block(self, source_address, target_address, amount, direction, sig, key, username):

        data = {
            'source_address': source_address,
            'target_address': target_address,
            'amount': amount,
            'direction': direction
        }

        if not self.has_stored_key(source_address) and not self.has_stored_username(source_address):
            if key is not None and username is not None:
                if self.validate_address(key, source_address):
                    self.store_key(source_address, key)
                    self.store_username(source_address, username)
                    new_block = self.create_generic_block(data)
                    self.add_create_block(new_block, source_address, target_address)
                    return new_block
                else:
                    raise BlockchainError('Public key is not valid')
            else:
                raise BlockchainError('You must provide a public key and username on your first transaction')

        if self.validate_sig(self.address_public_key_dict[source_address], sig,
                             str(source_address) + str(target_address) + str(amount)):
            new_block = self.create_generic_block(data)
            self.add_create_block(new_block, source_address, target_address)
            return new_block
        else:
            raise BlockchainError('Signature not validated')

    def finalize_request_block(self, request_block_hash, source_address, target_address, accepted):
        # todo add lock
        if request_block_hash in self.unaccepted_payments:
            request_data = {
                'request_block_hash': request_block_hash,
                'accepted': accepted,
            }
            new_block = self.create_generic_block(request_data)
            self.unaccepted_payments.remove(request_block_hash)
            self.finalized_payments[request_block_hash] = new_block.hash

            status = 'rejected'

            if accepted:
                status = 'accepted'

            source_dict = self.address_transactions_dict[source_address][request_block_hash]
            source_dict['status'] = status
            target_dict = self.address_transactions_dict[target_address][request_block_hash]
            target_dict['status'] = status

            return new_block
        else:
            raise BlockchainError('Block already finalized', self.finalized_payments[request_block_hash])

    def accept_request_block(self, request_block_hash, sig, key, username):

        transaction_block = self.retrieve_block(request_block_hash)
        source_address = transaction_block.data['source_address']
        target_address = transaction_block.data['target_address']

        if not self.has_stored_key(target_address) and not self.has_stored_username(target_address):
            if key is not None and username is not None:
                if self.validate_address(key, target_address):
                    self.store_key(target_address, key)
                    self.store_username(target_address, username)
                    return self.finalize_request_block(request_block_hash, source_address, target_address, True)
                else:
                    raise BlockchainError('Public key is not valid')
            else:
                raise BlockchainError('You must provide a public key and username on your first transaction')

        if self.validate_sig(self.address_public_key_dict[target_address], sig, request_block_hash):
            return self.finalize_request_block(request_block_hash, source_address, target_address, True)
        else:
            raise BlockchainError('Signature not validated')

    def revoke_request_block(self, request_block_hash, sig):

        transaction_block = self.retrieve_block(request_block_hash)
        source_address = transaction_block.data['source_address']
        target_address = transaction_block.data['target_address']

        if self.has_stored_key(source_address):
            if self.validate_sig(self.address_public_key_dict[source_address], sig, request_block_hash):
                return self.finalize_request_block(request_block_hash, source_address, target_address, False)
            else:
                if self.has_stored_key(target_address):
                    if self.validate_sig(self.address_public_key_dict[target_address], sig, request_block_hash):
                        return self.finalize_request_block(request_block_hash, source_address, target_address, False)

        else:
            raise BlockchainError('Public key not available')

    def retrieve_block(self, block_hash):
        if block_hash in self.block_hash_dict:
            return self.block_hash_dict[block_hash]
        else:
            raise BlockchainError('Block does not exist')

    def retrieve_address_transactions(self, address):
        if address in self.address_transactions_dict:
            return self.address_transactions_dict[address]
        else:
            return {}

    def validate_address(self, key, address):
        return address == str(arky.core.crypto.getAddress(key))

    def validate_sig(self, key, sig, data):
        # sha = hasher.sha256()
        # sha.update(data)

        # key = RSA.importKey(key)

        # cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)

        # return cipher.decrypt(sig) == sha.hexdigest
        return True

    def has_stored_key(self, address):
        return address in self.address_public_key_dict

    def has_stored_username(self, address):
        return address in self.address_username_dict

    def store_key(self, address, key):
        self.address_public_key_dict[address] = key

    def store_username(self, address, username):
        self.address_username_dict[address] = username

    def get_username(self, address):
        if self.has_stored_username(address):
            return self.address_username_dict[address]
        else:
            return 'Unknown'

    def get_users(self):
        return list(self.address_username_dict.values())

    def create_username(self, name):
        uid = randint(1000, 9999)
        username = name + str(uid)
        while username in self.get_users():
            uid = randint(1000, 9999)
            username = name + str(uid)
        return username


class BlockchainError(Exception):
    pass
