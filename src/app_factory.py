import os
import sys
from uuid import uuid4
from flask import Flask, jsonify, request

CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.dirname(CURRENT_DIR)
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from blockchain import Blockchain

def create_app():
    blockchain = Blockchain()
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

    node_address = str(uuid4()).replace('-', '')

    @app.route('/mine_block', methods=['GET'])
    def mine_block():
        previous_block = blockchain.get_previous_block()
        previous_proof = previous_block['proof']
        proof = blockchain.proof_of_work(previous_proof)
        previous_hash = blockchain.hash(previous_block)
        blockchain.add_transaction(sender=node_address, receiver='Lopes', amount=10)
        block = blockchain.create_block(proof, previous_hash)

        response = {
            'message': 'Block mined!',
            'index': block['index'],
            'timestamp': block['timestamp'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
            'transactions': block['transactions']
        }
        return jsonify(response), 200

    @app.route('/get_chain', methods=['GET'])
    def get_chain():
        response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain)
        }
        return jsonify(response), 200

    @app.route('/is_valid', methods=['GET'])
    def is_valid():
        is_valid = blockchain.is_chain_valid(blockchain.chain)
        if is_valid:
            response = {'message': 'All good. The Blockchain is valid.'}
        else:
            response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
        return jsonify(response), 200

    @app.route('/add_transaction', methods=['POST'])
    def add_transaction():
        json_data = request.get_json()
        transaction_keys = ['sender', 'receiver', 'amount']

        if not json_data or not all(key in json_data for key in transaction_keys):
            return 'Some elements of the transaction are missing', 400

        index = blockchain.add_transaction(json_data['sender'], json_data['receiver'], json_data['amount'])
        response = {'message': f'This transaction will be added to Block {index}'}
        return jsonify(response), 201

    @app.route('/connect_node', methods=['POST'])
    def connect_node():
        json_data = request.get_json()
        nodes = json_data.get('nodes') if json_data else None

        if nodes is None:
            return 'No node', 400

        for node in nodes:
            blockchain.add_node(node)

        response = {
            'message': 'All nodes are now connected. The chain now contains the following nodes:',
            'total_nodes': list(blockchain.nodes)
        }
        return jsonify(response), 201

    @app.route('/replace_chain', methods=['GET'])
    def replace_chain():
        is_chain_replaced = blockchain.replace_chain()
        if is_chain_replaced:
            response = {
                'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                'new_chain': blockchain.chain
            }
        else:
            response = {
                'message': 'All good. The chain is the largest one.',
                'actual_chain': blockchain.chain
            }
        return jsonify(response), 200

    return app