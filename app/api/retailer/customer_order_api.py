# app/api/retailer/retailer_dynamic_api.py
from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

BASE_URL = "http://151.185.41.194:8000/orders/retailer/"

@router.get("/get_orders/{retailer_id}", tags=["Customer orders"])
async def get_orders(retailer_id: int):
    """
    Fetch orders from external API dynamically by retailer_id
    """
    url = f"{BASE_URL}{retailer_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, 
                                detail=f"Error fetching data: {exc.response.text}")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, 
                                detail=f"Request failed: {exc}")
    
    return response.json()
