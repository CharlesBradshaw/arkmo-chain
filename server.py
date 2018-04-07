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
                                                  params['direction'], params['sig'], params.get('key', None))
        return json.dumps({'new_block': result.__dict__})
    except BlockchainError as e:
        return str(e), 403


@app.route("/blockchain/request/accept", methods=['POST'])
def block_request_accept():
    data = request.data.decode("utf-8")
    params = json.loads(data)

    try:
        result = block_chain.accept_request_block(params['hash'], params['sig'], params.get('key', None))
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


if __name__ == "__main__":
    app.run()
