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
