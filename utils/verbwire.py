import os
import json
import requests
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables
load_dotenv()
VERBWIRE_API_KEY = os.getenv("VERBWIRE_API_KEY")

VERBWIRE_BASE_URL = "https://api.verbwire.com/v1"

# Endpoints
MINT_FROM_METADATA_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/mint/quickMintFromMetadata"
TRANSACTION_DETAILS_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/userOps/transactionDetails"
OWNED_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/data/owned"
UPDATE_METADATA_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/update/updateTokenMetadata"
STORE_FILE_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/store/file"
NFT_DETAILS_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/data/nftDetails"
STORE_AS_METADATA_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/store/metadataFromImage"


def mint_nft_from_metadata_url(metadata_url, wallet_address, chain="sepolia"):
    """
    Mints an NFT from a metadata URL using Verbwire's quickMintFromMetadataUrl endpoint.
    """
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
    """
    Retrieves all NFTs owned by the specified wallet using Verbwire's /nft/data/owned
    """
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
    """
    Checks the status of a transaction using Verbwire's transactionDetails endpoint.
    """
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
    """
    Updates the metadata of an NFT on-chain using the /update/updateTokenMetadata endpoint.
    """
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

def store_file_as_metadata(file_path,name,description,chain = 'sepolia'):

    headers = {
        "X-API-Key": VERBWIRE_API_KEY,
        "accept": "application/json"
    }
    payload ={
        "name": name,
        "description": description
    }

    with open(file_path, "rb") as f:
        files = {"filePath": f}
        response = requests.post(STORE_AS_METADATA_ENDPOINT, data=payload,headers = headers, files=files)

    try:
        json_resp = response.json()
        pprint(json_resp)  # For debugging
        return json_resp
    except Exception:
        return {
            "error": "Failed to parse JSON from Verbwire response.",
            "raw": response.text
        }



def upload_file_to_ipfs(file_path):
    """
    Uploads a local file to IPFS using Verbwire's store/file endpoint.
    Typically used for images or JSON metadata.
    """
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

def get_nft_details(contract_address, token_id, chain="sepolia", populate_metadata=True):
    """
    Fetches detailed info about a specific NFT, including on-chain metadata if populateMetadata=true.
    Returns a dict like:
    {
      "nft_details": {
        "name": "...",
        "symbol": "...",
        "ownerOf": "...",
        "metadata": {
          "name": "...",
          "description": "...",
          "image": "...",
          ...
        }
      }
    }
    or { "error": "..." } if something goes wrong.
    """
    headers = {
        "X-API-Key": VERBWIRE_API_KEY,
        "accept": "application/json"
    }

    params = {
        "contractAddress": contract_address,
        "tokenId": token_id,
        "chain": chain,
        "populateMetadata": "true" if populate_metadata else "false"
    }

    response = requests.get(NFT_DETAILS_ENDPOINT, headers=headers, params=params)
    try:
        return response.json()
    except Exception:
        return {
            "error": "Failed to parse JSON from Verbwire response.",
            "raw": response.text
        }