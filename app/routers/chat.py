import httpx
import json
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from .. import schemas 

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat")
async def get_ai_response(request: schemas.ChatRequest):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                settings.AI_ORIGIN + "/chat",
                json={
                    "persona": request.persona,
                    "message": request.message
                }
            )
            response.raise_for_status()
            content = json.loads(response.content.decode("utf-8"))
            print("AI RAW RESPONSE:", content)
            msg = content.get("message")
            print(msg)
            return {"message": msg}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI service timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"AI service returned error: {e.response.text}"
        )
    except httpx.RequestError as e:
        print("HTTPX REQUEST ERROR:", repr(e))
        raise HTTPException(status_code=503, detail=f"AI service request failed: {str(e)}")   
    