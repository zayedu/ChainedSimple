from pprint import pprint
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
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
    upload_file_to_ipfs,
    get_nft_details  # <-- We import this to fetch the NFT's metadata
)

app = Flask(__name__)
CORS(app)

@app.route('/login', methods=['POST'])
def login():
    """
    User provides a wallet address, we fetch all NFTs they own.
    Expects JSON: { "wallet_address": "<address>" }
    """
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
        }), 200

    return jsonify({
        "authenticated": True,
        "wallet_address": wallet_address,
        "nfts": nfts_list
    }), 200


@app.route('/mint_file_nft', methods=['POST'])
def mint_file_nft():
    """
    The user uploads a file -> we upload to IPFS -> we create minimal metadata referencing that file
    -> we also upload that metadata to IPFS -> we mint an NFT from that metadata to the user's wallet.

    Form-data:
      wallet_address=...
      chain=sepolia (optional)
      file=@someLocalFile
    """
    wallet_address = request.form.get("wallet_address")
    chain = request.form.get("chain", "sepolia")

    if not wallet_address:
        return jsonify({"error": "wallet_address is required"}), 400
    if 'file' not in request.files:
        return jsonify({"error": "No file in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 1. Upload the raw file to IPFS
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

    # 2. Create a minimal metadata JSON that references the file
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

    # 3. Upload that JSON to IPFS
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

    # 4. Mint NFT from the metadata IPFS URL
    mint_resp = mint_nft_from_metadata_url(metadata_ipfs_url, wallet_address, chain=chain)

    return jsonify({
        "minted": True,
        "wallet_address": wallet_address,
        "metadata_ipfs_url": metadata_ipfs_url,
        "mint_response": mint_resp
    }), 200


@app.route('/check_status', methods=['POST'])
def check_status():
    """
    Check the status of a minting transaction by ID.
    Expects JSON: { "transaction_id": "...someTxID..." }
    """
    data = request.get_json()
    transaction_id = data.get("transaction_id")

    if not transaction_id:
        return jsonify({"error": "transaction_id is required"}), 400

    resp = check_transaction_status(transaction_id)
    pprint(resp)
    return jsonify(resp), 200


@app.route('/update_metadata', methods=['POST'])
def update_metadata_endpoint():
    """
    Directly updates an NFT's on-chain metadata to a new URI.

    Expects JSON:
    {
      "contract_address": "...",
      "token_id": "...",
      "new_token_uri": "...",
      "chain": "sepolia" (optional)
    }
    """
    data = request.get_json()
    contract_address = data.get("contract_address")
    token_id = data.get("token_id")
    new_token_uri = data.get("new_token_uri")
    chain = data.get("chain", "sepolia")

    if not contract_address or not token_id or not new_token_uri:
        return jsonify({
            "error": "contract_address, token_id, and new_token_uri are required"
        }), 400

    resp = update_nft_metadata(
        contract_address=contract_address,
        token_id=token_id,
        new_token_uri=new_token_uri,
        chain=chain
    )
    pprint(resp)
    return jsonify(resp), 200


@app.route('/view_nft_image', methods=['POST'])
def view_nft_image():
    """
    Calls Verbwire's getNFTDetails endpoint to retrieve the NFT metadata,
    then redirects to the 'image' URL in the metadata.

    Expects JSON:
    {
      "contract_address": "<NFT contract>",
      "token_id": "<NFT token ID>",
      "chain": "sepolia" (optional)
    }

    If found, we do a 302 redirect to the 'image' link from the metadata.
    """
    data = request.get_json()
    contract_address = data.get("contract_address")
    token_id = data.get("token_id")
    chain = data.get("chain", "sepolia")

    if not contract_address or not token_id:
        return jsonify({"error": "contract_address and token_id are required"}), 400

    # Step 1: Get NFT details from Verbwire
    from utils.verbwire import get_nft_details
    details = get_nft_details(contract_address, token_id, chain=chain, populate_metadata=True)
    if "error" in details:
        return jsonify({"error": details["error"]}), 400

    nft_details = details.get("nft_details", {})
    metadata = nft_details.get("metadata", {})
    image_url = metadata.get("image")

    if not image_url:
        return jsonify({
            "error": "No image URL found in NFT metadata.",
            "metadata": metadata
        }), 400

    # Step 2: Redirect the user to that image URL
    return redirect(image_url, code=302)


if __name__ == '__main__':
    app.run(debug=True)
