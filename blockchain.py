import hashlib as hasher
from datetime import datetime
class Block:
  def __init__(self, data, previous_hash):
    self.data = data
    self.previous_hash = previous_hash
    self.hash = self.hash_block()
  
  def hash_block(self):
    sha = hasher.sha256()
    sha.update(str(self.data) + str(self.previous_hash))
    return sha.hexdigest()




class Blockchain:

  def __init__():
    self.unaccepted_payments = Set()

    genesis_block_data = {}
    genesis_block = create_generic_block(self,genesis_block_data,0)
    self.chain = [genesis_block]


  def create_generic_block(self, data):

    data['timestamp'] = datetime.now(),

    new_block = Block(data,self.chain[-1].hash)
    self.chain.append(new_block)
    return new_block

  def create_request_block(self,from_address,to_address,ammount):

    data = {
      'from_address': from_address,
      'to_address': to_address,
      'ammount': ammount,
    }
    new_block = self.create_generic_block(data)
    self.unaccepted_payments.add(new_block.hash)
    #hash dict

    return new_block


  def finalize_request_block(self,request_block_hash, accepted):
    # todo add lock
    if request_block_hash in self.unaccepted_payments:
      request_data = { 
        'request_block_hash' : request_block_hash,
        'accepted': accepted,
      }
      new_block = create_generic_block(self,request_data)
      self.unaccepted_payments.remove(request_block_hash)
      return new_block
    else:
      raise Exception('all hell')

  def accept_request_block(request_block_hash):
    return self.finalize_request_block(request_block_hash, True)

  def revoke_request_block(request_block_hash):
    return self.finalize_request_block(request_block_hash, False)





