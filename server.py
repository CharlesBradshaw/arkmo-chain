import json

from flask import Flask, request
from flask_cors import CORS

from blockchain import Blockchain

app = Flask(__name__)
CORS(app)

block_chain = Blockchain()


@app.route("/blockchain/create/request", methods=['POST'])
def blockCreateRequest():
    from_address = request.frm.decode('utf-8')
    to_address = request.to.decode('utf-8')
    amount = request.amt.decode('utf-8')

    result = block_chain.create_request_block(from_address, to_address, amount)
    return json.dumps({'new_block', result.__dict__})


if __name__ == "__main__":
    app.run()
