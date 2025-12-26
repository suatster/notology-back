import httpx
from fastapi import APIRouter, HTTPException
from app.core.config import settings

router = APIRouter(prefix="/ai", tags=["AI"])

# @router.get("/chat")
# def get_ai_response():
#     try:
#         response = requests.get(settings.AI_ORIGIN)
#         response.raise_for_status()
#         return {"message": response.text}
#     except requests.RequestException as e:
#         raise HTTPException(
#             status_code=503,
#             detail=f"AI service error: {e}"
#         )
    
# import httpx
# from fastapi import APIRouter, HTTPException
# from app.core.config import settings

# router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat")
async def get_ai_response():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(settings.AI_ORIGIN)
            response.raise_for_status()
            return {"message": response.text}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI service timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"AI service returned error: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service request failed: {str(e)}")    
    