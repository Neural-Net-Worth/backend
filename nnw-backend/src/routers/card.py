from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from config import settings
from integration.card.card_issuer import CardIssuer
from integration.card.mock_card_issuer import MockCardIssuer, CardDetails
from integration.card.stripe_card_issuer import StripeCardIssuer

router = APIRouter()


class CreateCardRequest(BaseModel):
    cardholder_id: str
    purchase_amount: int  # in cents (e.g., 1000 for $10.00)
    currency: str = "usd"
    merchant_id: str
    allowed_categories: Optional[List[str]] = None
    blocked_categories: Optional[List[str]] = None
    expiration_seconds: int = 3600  # Default expiration window of 1 hour


def get_card_issuer() -> CardIssuer:
    # For an MVP or testing, we use the mock adapter.
    # In production, switch to the StripeCardIssuer.
    if settings.ENV == "production":
        return StripeCardIssuer(settings.STRIPE_API_KEY)
    return MockCardIssuer()


@router.post("/cards", response_model=CardDetails)
async def create_card(
    request: CreateCardRequest,
    card_issuer: CardIssuer = Depends(get_card_issuer)
):
    try:
        card_response = card_issuer.create_card(
            cardholder_id=request.cardholder_id,
            purchase_amount=request.purchase_amount,
            currency=request.currency,
            merchant_id=request.merchant_id,
            allowed_categories=request.allowed_categories,
            blocked_categories=request.blocked_categories,
            expiration_seconds=request.expiration_seconds,
        )

        card_details = card_issuer.get_card_details(card_response.id)
        return card_details
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
