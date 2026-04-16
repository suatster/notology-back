from fastapi import APIRouter, HTTPException
from app.services.quotes_service import QuotesService

router = APIRouter(prefix="/quotes", tags=["Quotes"])

service = QuotesService()

@router.get("/random")
async def fetch_random_quote():
    try:
        return await service.get_random_quote()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
