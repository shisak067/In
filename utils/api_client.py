# utils/api_client.py
import asyncio
import aiohttp
import json
from typing import Dict
from config import DEFAULT_APIS
from utils.helpers import api_settings

async def make_api_request(url: str) -> Dict:
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}", "status_code": response.status}
    except asyncio.TimeoutError:
        return {"error": "Request timeout", "status_code": 408}
    except Exception as e:
        return {"error": str(e), "status_code": 500}

def is_api_enabled(service: str) -> bool:
    return api_settings.get("apis", {}).get(service, {}).get("enabled", True)

def get_api_url(service: str) -> str:
    return api_settings.get("apis", {}).get(service, {}).get("url", DEFAULT_APIS.get(service, ""))

async def search_indian_number(number: str, mongo) -> Dict:
    number = ''.join(filter(str.isdigit, number))
    if len(number) < 10:
        return {"error": "Invalid number (min 10 digits)", "query": number}
    blocked = mongo.get_blocked_number(number)
    if blocked:
        return {"error": f"Number blocked", "blocked": True}
    if not is_api_enabled("num"):
        return {"error": "API disabled"}
    url = f"{get_api_url('num')}{number}"
    data = await make_api_request(url)
    data["query"] = number
    return data

async def search_indian_aadhar(aadhar: str, mongo) -> Dict:
    aadhar = ''.join(filter(str.isdigit, aadhar))
    if len(aadhar) != 12:
        return {"error": "Invalid Aadhar (12 digits)", "query": aadhar}
    if not is_api_enabled("aadhar"):
        return {"error": "API disabled"}
    url = f"{get_api_url('aadhar')}{aadhar}"
    data = await make_api_request(url)
    data["query"] = aadhar
    return data

async def search_pak_number(number: str, mongo) -> Dict:
    number = ''.join(filter(str.isdigit, number))
    if len(number) < 10:
        return {"error": "Invalid Pakistan number", "query": number}
    if not is_api_enabled("pak_num"):
        return {"error": "API disabled"}
    url = f"{get_api_url('pak_num')}{number}"
    data = await make_api_request(url)
    data["query"] = number
    return data

async def search_pak_cnic(cnic: str, mongo) -> Dict:
    cnic = ''.join(filter(str.isdigit, cnic))
    if len(cnic) != 13:
        return {"error": "Invalid CNIC (13 digits)", "query": cnic}
    if not is_api_enabled("pak_cnic"):
        return {"error": "API disabled"}
    url = f"{get_api_url('pak_cnic')}{cnic}"
    data = await make_api_request(url)
    data["query"] = cnic
    return data

async def search_pak_police(number: str, mongo) -> Dict:
    number = ''.join(filter(str.isdigit, number))
    if len(number) < 10:
        return {"error": "Invalid number", "query": number}
    if not is_api_enabled("pak_police"):
        return {"error": "API disabled"}
    url = f"{get_api_url('pak_police')}{number}"
    data = await make_api_request(url)
    data["query"] = number
    return data

async def search_gst_billing(gstin: str, mongo) -> Dict:
    gstin = gstin.strip().upper()
    if len(gstin) != 15:
        return {"error": "Invalid GSTIN (15 chars)", "query": gstin}
    if not is_api_enabled("gst_billing"):
        return {"error": "API disabled"}
    url = f"{get_api_url('gst_billing')}{gstin}"
    data = await make_api_request(url)
    data["query"] = gstin
    return data

async def search_pan_gst(pan: str, mongo) -> Dict:
    pan = pan.strip().upper()
    if len(pan) != 10:
        return {"error": "Invalid PAN (10 chars)", "query": pan}
    if not is_api_enabled("pan_gst"):
        return {"error": "API disabled"}
    url = f"{get_api_url('pan_gst')}{pan}"
    data = await make_api_request(url)
    data["query"] = pan
    return data

async def search_aadhar_family(aadhar: str, mongo) -> Dict:
    aadhar = ''.join(filter(str.isdigit, aadhar))
    if len(aadhar) != 12:
        return {"error": "Invalid Aadhar (12 digits)", "query": aadhar}
    if not is_api_enabled("aadhar_family"):
        return {"error": "API disabled"}
    url = f"{get_api_url('aadhar_family')}{aadhar}"
    data = await make_api_request(url)
    data["query"] = aadhar
    return data
