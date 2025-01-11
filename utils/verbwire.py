import os
import json
import requests
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables (VERBWIRE_API_KEY, etc.)
load_dotenv()
VERBWIRE_API_KEY = os.getenv("VERBWIRE_API_KEY")

pprint(VERBWIRE_API_KEY)

VERBWIRE_BASE_URL = "https://api.verbwire.com/v1"

#Endpoints (just minting an nft for rn)

MINT_FROM_METADATA_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/mint/quickMintFromMetadata"
OWNED_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/data/owned"
TRANSACTION_DETAILS_ENDPOINT = f"{VERBWIRE_BASE_URL}/nft/userOps/transactionDetails"

def mint_nft_from_metadata_url(metadata_url, wallet_address, chain="sepolia"):
    """
    use quick mint from metadata url endpoint to mint an NFT and associate with users wallet address
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
    Retrieves all NFTs owned by the specified wallet using Verbwire's /nft/data/owned.
    Defaults to chain=sepolia, tokenType=nft721, ASC sort, limit=1000.
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