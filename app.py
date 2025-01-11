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

@app.route('/mint_file_nft', methods=['POST'])
def mint_file_nft():

    wallet_address = request.form.get("wallet_address")
    chain = request.form.get("chain", "sepolia")

    if not wallet_address:
        return jsonify({"error": "wallet_address is required"}), 400
    if 'file' not in request.files:
        return jsonify({"error": "No file in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = f"/tmp/{file.filename}"
    file.save(file_path)
    try:
        ipfs_resp = upload_file_to_ipfs(file_path)
    finally:
        os.remove(file_path)

    if "error" in ipfs_resp:
        return jsonify({
            "error": "Failed to upload file to IPFS",
            "details": ipfs_resp
        }), 400

    ipfs_url = ipfs_resp.get("ipfs_storage", {}).get("ipfs_url")
    if not ipfs_url:
        return jsonify({
            "error": "Could not parse IPFS URL from response",
            "response": ipfs_resp
        }), 400

    metadata = {
        "name": "My Uploaded File",
        "description": "NFT representing a user-uploaded file",
        "image": ipfs_url,
        "date_created": datetime.utcnow().isoformat()
    }

    timestamp_str = str(int(time.time()))
    temp_metadata_file = f"/tmp/metadata_{timestamp_str}.json"
    with open(temp_metadata_file, 'w') as f:
        json.dump(metadata, f)

    try:
        meta_ipfs_resp = upload_file_to_ipfs(temp_metadata_file)
    finally:
        os.remove(temp_metadata_file)

    if "error" in meta_ipfs_resp:
        return jsonify({
            "error": "Failed to upload metadata JSON to IPFS",
            "details": meta_ipfs_resp
        }), 400

    metadata_ipfs_url = meta_ipfs_resp.get("ipfs_storage", {}).get("ipfs_url")
    if not metadata_ipfs_url:
        return jsonify({
            "error": "Could not parse IPFS URL for metadata",
            "response": meta_ipfs_resp
        }), 400

    mint_resp = mint_nft_from_metadata_url(metadata_ipfs_url, wallet_address, chain=chain)

    return jsonify({
        "minted": True,
        "wallet_address": wallet_address,
        "metadata_ipfs_url": metadata_ipfs_url,
        "mint_response": mint_resp
    }), 200

#TODO: Check the status when we send a mint request
@app.route('/check_status', methods=['POST'])
def check_status():

    data = request.get_json()
    transaction_id = data.get("transaction_id")

    if not transaction_id:
        return jsonify({"error": "transaction_id is required"}), 400

    resp = check_transaction_status(transaction_id)
    pprint(resp)
    return jsonify(resp), 200


#TODO: Update the metadata of a token