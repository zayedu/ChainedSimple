from pprint import pprint
from flask import Flask, request, jsonify, CORS
import os
import json
import time
from datetime import datetime

# Import Verbwire helper functions
from utils.verbwire import (
    mint_nft_from_metadata_url,
    get_wallet_nfts,
    check_transaction_status,
    update_nft_metadata,
    upload_file_to_ipfs
)

app = Flask(__name__)
CORS(app)

'''
Basically here were gonna have a user give their wallet address and then we use verbwire api to find their nfts
'''

@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()
    wallet_address = data.get("wallet_address")
    if not wallet_address:
        return jsonify({"error": "wallet_address is required"}), 400

    nfts_response = get_wallet_nfts(wallet_address)
    pprint(nfts_response)

    if "error" in nfts_response:
        return jsonify({
            "authenticated": False,
            "error": nfts_response["error"]
        }), 400

    nfts_list = nfts_response.get("nfts", [])
    if not nfts_list:
        return jsonify({
            "authenticated": False,
            "error": "No NFTs found for this wallet address.",
            "nfts": []
        }), 200  #

    return jsonify({
        "authenticated": True,
        "wallet_address": wallet_address,
        "nfts": nfts_list
    }), 200

#TODO: We need to mint an nft when the user uploads a file

#TODO: Check the status when we send a mint request

#TODO: Update the metadata of a token