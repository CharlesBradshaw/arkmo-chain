import json

from flask import Flask, request
from flask_cors import CORS

from blockchain import Blockchain, BlockchainError

app = Flask(__name__)
CORS(app)

block_chain = Blockchain()


@app.route("/blockchain/request/create", methods=['POST'])
def block_request_create():
    data = request.data.decode("utf-8")
    params = json.loads(data)

    try:
        result = block_chain.create_request_block(params['source'], params['target'], params['amount'],
                                                  params['direction'], params['sig'], params.get('key', None),
                                                  params.get('username', None))
        return json.dumps({'new_block': result.__dict__})
    except BlockchainError as e:
        return str(e), 403


@app.route("/blockchain/request/accept", methods=['POST'])
def block_request_accept():
    data = request.data.decode("utf-8")
    params = json.loads(data)

    try:
        result = block_chain.accept_request_block(params['hash'], params['sig'], params.get('key', None),
                                                  params.get('username', None))
        return json.dumps({'new_block': result.__dict__})
    except BlockchainError as e:
        return str(e), 403


@app.route("/blockchain/request/revoke", methods=['POST'])
def block_request_revoke():
    data = request.data.decode("utf-8")
    params = json.loads(data)

    try:
        result = block_chain.revoke_request_block(params['hash'], params['sig'])
        return json.dumps({'new_block': result.__dict__})
    except BlockchainError as e:
        return str(e), 403


@app.route("/blockchain/retrieve", methods=['GET'])
def block_retrieve():
    hash_param = request.args.get('hash')

    try:
        result = block_chain.retrieve_block(hash_param)
        return json.dumps({'block': result.__dict__})
    except BlockchainError as e:
        return str(e), 404


@app.route("/blockchain/transactions", methods=['GET'])
def block_transactions():
    address_param = request.args.get('address')

    result = block_chain.retrieve_address_transactions(address_param)
    return json.dumps({'transactions': result})


@app.route("/blockchain/dev", methods=['GET'])
def dev():
    return '{"transactions": {"9bfe2c0573390e7f8484e65155a24ba2de5e8984a9743e72e6417a63788a639f": {"block": {"data": ' \
           '{"source_address": "D74BQWJKBWnHGLWL2FNrLn1oynnB8Rzeak", "target_address": "asdf", "amount": 10, ' \
           '"direction": "SourceToTarget", "timestamp": "2018-04-07 21:38:16.476296"}, "previous_hash": ' \
           '"b14607cc870d6b301e58414970bcc4c307d897cebc3b1f6849e1cf4ad1057199", "hash": ' \
           '"9bfe2c0573390e7f8484e65155a24ba2de5e8984a9743e72e6417a63788a639f"}, "status": "rejected", ' \
           '"source_username": "testy", "target_username": "bill"}, ' \
           '"07a96f947536262bbd2ef61bf707ea9f6461188e0126df310c239f712627ce9e": {"block": {"data": {"source_address": ' \
           '"D74BQWJKBWnHGLWL2FNrLn1oynnB8Rzeak", "target_address": "jkl", "amount": 100, "direction": ' \
           '"SourceToTarget", "timestamp": "2018-04-07 21:38:41.000783"}, "previous_hash": ' \
           '"9bfe2c0573390e7f8484e65155a24ba2de5e8984a9743e72e6417a63788a639f", "hash": ' \
           '"07a96f947536262bbd2ef61bf707ea9f6461188e0126df310c239f712627ce9e"}, "status": "pending", ' \
           '"source_username": "testy", "target_username": "bob"}, ' \
           '"173417c3bdc9c5f1fac5ba88984e50acaed2b8cc1aef71f1e0cd03b1fe5d35e2": {"block": {"data": {"source_address": ' \
           '"D74BQWJKBWnHGLWL2FNrLn1oynnB8Rzeak", "target_address": "jkl", "amount": 100, "direction": ' \
           '"TargetToSource", "timestamp": "2018-04-07 21:38:51.575147"}, "previous_hash": ' \
           '"07a96f947536262bbd2ef61bf707ea9f6461188e0126df310c239f712627ce9e", "hash": ' \
           '"173417c3bdc9c5f1fac5ba88984e50acaed2b8cc1aef71f1e0cd03b1fe5d35e2"}, "status": "rejected", ' \
           '"source_username": "testy", "target_username": "Unknown"}}} '


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
