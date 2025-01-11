from pprint import pprint
from flask import Flask, render_template, request, redirect, url_for, jsonify
from utils.verbwire import get_wallet_nfts, update_nft_metadata
import os

# Import the refactored Verbwire helper functions
from utils.verbwire import (
    mint_nft_from_metadata_url,
    get_wallet_nfts,
    check_transaction_status,
    update_nft_metadata,
    upload_file_to_ipfs
)

app = Flask(__name__)

# MetaMask Login Page
@app.route("/")
def login():
    return render_template("login.html")

# Dashboard Page
@app.route("/dashboard", methods=["POST"])
def dashboard():
    wallet_address = request.form.get("wallet_address")

    if not wallet_address:
        return render_template("login.html", error="Wallet address is required.")

    # Fetch NFTs for the wallet
    nfts_response = get_wallet_nfts(wallet_address)

    if "error" in nfts_response:
        return render_template("login.html", error=nfts_response["error"])
    print(nfts_response)
    nfts = nfts_response.get("nfts", [])
    print(nfts)
    return render_template("dashboard.html", wallet_address=wallet_address, nfts=nfts)

@app.route('/register', methods=['POST'])
def register():
    """
    Mint an NFT via Verbwire using a metadata URL.
    Expects JSON:
    {
      "wallet_address": "<recipient_wallet>",
      "metadata_url": "<ipfs_or_https>",
      "chain": "<blockchain>"  (optional, defaults to "sepolia")
    }
    """
    data = request.get_json()
    wallet_address = data.get("wallet_address")
    metadata_url = data.get("metadata_url")
    chain = data.get("chain", "sepolia")

    if not wallet_address or not metadata_url:
        return jsonify({"error": "wallet_address and metadata_url are required"}), 400

    resp = mint_nft_from_metadata_url(metadata_url, wallet_address, chain=chain)
    pprint(resp)
    return jsonify(resp), 200


@app.route('/auth', methods=['POST'])
def auth_user():
    """
    Checks whether a given wallet has any NFTs (via Verbwire's /nft/data/owned).
    Expects JSON:
    {
      "wallet_address": "<address_to_verify>"
    }
    Returns the list of NFTs if any are found.
    """
    data = request.get_json()
    wallet_address = data.get("wallet_address")
    if not wallet_address:
        return jsonify({"error": "wallet_address is required"}), 400

    # Default to chain="sepolia" and tokenType="nft721"
    nfts_response = get_wallet_nfts(wallet_address)
    pprint(nfts_response)

    # If there's an error or the "nfts" list is empty, handle accordingly
    if "error" in nfts_response:
        # Means we got some error from Verbwire
        return jsonify({
            "authenticated": False,
            "error": nfts_response["error"]
        }), 400

    nfts_list = nfts_response.get("nfts", [])
    if not nfts_list:
        return jsonify({"authenticated": False, "error": "No NFTs found for this wallet address."}), 404

    return jsonify({
        "authenticated": True,
        "wallet_address": wallet_address,
        "nfts": nfts_list
    }), 200


@app.route('/check_status', methods=['POST'])
def check_status():
    """
    Check the status of a minting transaction by ID.
    Expects JSON:
    {
      "transaction_id": "<verbwire_transaction_id>"
    }
    """
    data = request.get_json()
    transaction_id = data.get("transaction_id")

    if not transaction_id:
        return jsonify({"error": "transaction_id is required"}), 400

    resp = check_transaction_status(transaction_id)
    pprint(resp)
    return jsonify(resp), 200


@app.route("/update_metadata", methods=["POST"])
def update_metadata():
    """
    Updates the metadata of an existing NFT.
    Handles both JSON and form data.
    """

    # Check if the data is coming as JSON or form data
    if request.is_json:
        # Handle JSON data
        data = request.get_json()
        contract_address = data.get("contract_address")
        token_id = data.get("token_id")
        new_token_uri = data.get("new_token_uri")
        chain = data.get("chain", "sepolia")  # Default to "sepolia"
    else:
        # Handle form data
        contract_address = request.form.get("contract_address")
        token_id = request.form.get("token_id")
        new_token_uri = request.form.get("new_token_uri")
        chain = request.form.get("chain", "sepolia")  # Default to "sepolia"

    # Validate required fields
    if not all([contract_address, token_id, new_token_uri]):
        return jsonify({"error": "contract_address, token_id, and new_token_uri are required"}), 400

    # Call the utility function to update NFT metadata
    update_response = update_nft_metadata(
        contract_address=contract_address,
        token_id=token_id,
        new_token_uri=new_token_uri,
        chain=chain
    )

    # Handle response from the utility function
    if "error" in update_response:
        return jsonify({"error": update_response["error"]}), 400

    # Redirect to the dashboard if using form data or return JSON response
    if not request.is_json:
        return redirect(url_for("dashboard"))
    
    return jsonify(update_response), 200



@app.route('/upload_file', methods=['POST'])
def upload_file():
    """
    Upload a local file to IPFS via Verbwire's /nft/store/file endpoint.
    Expects a multipart/form-data with { "file": <the_file> }
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = f"/tmp/{file.filename}"
    file.save(file_path)

    try:
        resp = upload_file_to_ipfs(file_path)
        pprint(resp)
        return jsonify(resp), 200
    finally:
        os.remove(file_path)

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    """
    Handles the upload page and processes file uploads.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', error="No file part in the request.")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', error="No selected file.")
        
        file_path = f"/tmp/{file.filename}"
        file.save(file_path)

        try:
            resp = upload_file_to_ipfs(file_path)
            # Add success data to pass to the template
            return render_template('upload.html', success=resp)
        finally:
            os.remove(file_path)
    
    return render_template('upload.html')

@app.route('/view_nft_image', methods=['GET'])
def view_nft_image():
    """
    Calls Verbwire's getNFTDetails endpoint to retrieve the NFT metadata,
    then redirects to the 'image' URL in the metadata.

    Query Parameters:
      - contract_address: NFT contract address
      - token_id: NFT token ID
      - chain: Blockchain network (default: "sepolia")
    """
    contract_address = request.args.get("contract_address")
    token_id = request.args.get("token_id")
    chain = request.args.get("chain", "sepolia")

    if not contract_address or not token_id:
        return jsonify({"error": "Missing contract_address or token_id"}), 400

    # Step 1: Fetch NFT details using the Verbwire helper
    from utils.verbwire import get_nft_details
    details = get_nft_details(contract_address, token_id, chain=chain, populate_metadata=True)

    if "error" in details:
        return jsonify({"error": details["error"]}), 400

    nft_details = details.get("nft_details", {})
    metadata = nft_details.get("metadata", {})
    image_url = metadata.get("image")

    if not image_url:
        return jsonify({"error": "Image URL not found in NFT metadata."}), 404

    # Step 2: Redirect to the image URL
    return redirect(image_url, code=302)



if __name__ == '__main__':
    app.run(debug=True)


