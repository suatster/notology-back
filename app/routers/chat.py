import httpx
import json
from fastapi import APIRouter, HTTPException, Query
from app.core.config import settings
from .. import schemas 

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat")
async def get_ai_response(request: schemas.ChatRequest):
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                settings.AI_ORIGIN + "/api/generate",
                json={
                    "model": "mistral:latest" if request.model == "freud" else "wizard-math:7b",
                    "prompt": request.prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            content = json.loads(response.content.decode("utf-8"))
            msg = content.get("response")
            return {"reply": msg}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI service timeout")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"AI service returned error: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service request failed: {str(e)}")   
