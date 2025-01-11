import os
import json
import requests
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables (VERBWIRE_API_KEY, etc.)
load_dotenv()
VERBWIRE_API_KEY = os.getenv("VERBWIRE_API_KEY")

VERBWIRE_BASE_URL = "https://api.verbwire.com/v1"

#### ENDPOINTS ####
MINT_FROM_METADATA_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/mint/quickMintFromMetadata"
TRANSACTION_DETAILS_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/userOps/transactionDetails"
OWNED_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/data/owned"
UPDATE_METADATA_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/update/updateTokenMetadata"
STORE_FILE_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/store/file"
NFT_DETAILS_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/data/nftDetails"


def mint_nft_from_metadata_url(metadata_url, wallet_address, chain="sepolia"):

    quickMintFromMetadataUrl_endpoint = f"{VERBWIRE_BASE_URL}/nft/mint/quickMintFromMetadataUrl"

    form_data = {
        "metadataUrl": (None, metadata_url),
        "recipientAddress": (None, wallet_address),
        "allowPlatformToOperateToken": (None, "true"),
        "chain": (None, chain)
    }

    headers = {
        "X-API-Key": VERBWIRE_API_KEY,
        "accept": "application/json"
    }

    response = requests.post(quickMintFromMetadataUrl_endpoint, files=form_data, headers=headers)
    try:
        return response.json()
    except Exception:
        return {
            "error": "Failed to parse JSON from Verbwire response.",
            "raw": response.text
        }


def get_wallet_nfts(wallet_address, chain="sepolia", token_type="nft721",
                    sort_direction="ASC", limit=1000, page=1):

    headers = {
        "X-API-Key": VERBWIRE_API_KEY,
        "accept": "application/json"
    }

    params = {
        "walletAddress": wallet_address,
        "chain": chain,
        "tokenType": token_type,
        "sortDirection": sort_direction,
        "limit": limit,
        "page": page
    }

    response = requests.get(OWNED_ENDPOINT, headers=headers, params=params)
    try:
        return response.json()
    except Exception:
        return {
            "error": "Failed to parse JSON from Verbwire response.",
            "raw": response.text
        }


def check_transaction_status(transaction_id):

    headers = {
        "X-API-Key": VERBWIRE_API_KEY,
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "transactionId": transaction_id
    }

    response = requests.post(TRANSACTION_DETAILS_ENDPOINT, headers=headers, data=data)
    try:
        return response.json()
    except Exception:
        return {
            "error": "Failed to parse JSON from Verbwire response.",
            "raw": response.text
        }


def update_nft_metadata(contract_address, token_id, new_token_uri, chain="sepolia"):

    headers = {
        "accept": "application/json",
        "X-API-Key": VERBWIRE_API_KEY
    }

    payload = {
        "contractAddress": contract_address,
        "tokenId": token_id,
        "newTokenURI": new_token_uri,
        "chain": chain
    }

    response = requests.post(UPDATE_METADATA_ENDPOINT, headers=headers, data=payload)
    try:
        return response.json()
    except Exception:
        return {
            "error": "Failed to parse JSON from Verbwire response.",
            "raw": response.text
        }


def upload_file_to_ipfs(file_path):

    headers = {
        "X-API-Key": VERBWIRE_API_KEY,
        "accept": "application/json"
    }

    with open(file_path, "rb") as f:
        files = {"filePath": f}
        response = requests.post(STORE_FILE_ENDPOINT, headers=headers, files=files)

    try:
        json_resp = response.json()
        pprint(json_resp)  # For debugging
        return json_resp
    except Exception:
        return {
            "error": "Failed to parse JSON from Verbwire response.",
            "raw": response.text
        }