import hashlib as hasher
import json
from datetime import datetime


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
        self.hash_dict = {}
        self.address_dict = {}
        self.create_genesis_block()

    def create_genesis_block(self):
        data = {}
        new_block = Block(data, 0)
        self.chain.append(new_block)
        self.hash_dict[new_block.hash] = new_block
        return new_block

    def create_generic_block(self, data):

        new_block = Block(data, self.chain[-1].hash)
        self.chain.append(new_block)
        self.hash_dict[new_block.hash] = new_block
        return new_block

    def create_request_block(self, from_address, to_address, amount, sig, key):

        data = {
            'from_address': from_address,
            'to_address': to_address,
            'amount': amount,
        }

        if not self.has_stored_key(from_address):
            if key is not None:
                if self.validate_address(key, from_address):
                    self.store_key(from_address, key)
                    new_block = self.create_generic_block(data)
                    self.unaccepted_payments.add(new_block.hash)
                    return new_block
                else:
                    raise BlockchainError('Signature is not valid')
            else:
                raise BlockchainError('You must provide a public key on your first transaction')

        if self.validate_sig(self.address_dict[from_address], sig):
            new_block = self.create_generic_block(data)
            self.unaccepted_payments.add(new_block.hash)
            return new_block
        else:
            raise BlockchainError('Signature not validated')

    def finalize_request_block(self, request_block_hash, accepted):
        # todo add lock
        if request_block_hash in self.unaccepted_payments:
            request_data = {
                'request_block_hash': request_block_hash,
                'accepted': accepted,
            }
            new_block = self.create_generic_block(request_data)
            self.unaccepted_payments.remove(request_block_hash)
            self.finalized_payments[request_block_hash] = new_block.hash
            return new_block
        else:
            raise BlockchainError('Block already finalized', self.finalized_payments[request_block_hash])

    def accept_request_block(self, request_block_hash, sig, key):

        transaction_block = self.retrieve_block(request_block_hash)
        to_address = transaction_block.data['to_address']

        if not self.has_stored_key(to_address):
            if key is not None:
                if self.validate_address(key, to_address):
                    self.store_key(to_address, key)
                    return self.finalize_request_block(request_block_hash, True)
                else:
                    raise BlockchainError('Signature is not valid')
            else:
                raise BlockchainError('You must provide a public key on your first transaction')

        if self.validate_sig(self.address_dict[to_address], sig):
            return self.finalize_request_block(request_block_hash, True)
        else:
            raise BlockchainError('Signature not validated')

    def revoke_request_block(self, request_block_hash, sig):

        transaction_block = self.retrieve_block(request_block_hash)
        from_address = transaction_block.data['from_address']

        if self.has_stored_key(from_address):
            if self.validate_sig(self.address_dict[from_address], sig):
                return self.finalize_request_block(request_block_hash, False)
            else:
                raise BlockchainError('Signature not validated')
        else:
            raise BlockchainError('Public key not available')

    def retrieve_block(self, block_hash):
        if block_hash in self.hash_dict:
            return self.hash_dict[block_hash]
        else:
            raise BlockchainError('Block does not exist')

    def validate_address(self, key, address):
        return True

    def validate_sig(self, key, sig):
        return True

    def has_stored_key(self, address):
        return address in self.address_dict

    def store_key(self, address, key):
        self.address_dict[address] = key


class BlockchainError(Exception):
    pass
