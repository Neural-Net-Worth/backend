import uuid
import random
from datetime import datetime, timedelta
from typing import List, Optional
from .card_issuer import CardIssuer
from pydantic import BaseModel


class CardDetails(BaseModel):
    card_number: str
    exp_date: str
    cvv: str
    name: str
    billing_address: str


class CardCreatedResponse(BaseModel):
    id: str
    cardholder: str
    last4: str
    purchase_limit: int
    currency: str
    merchant_id: str
    usage: str
    created: str
    provider: str
    expiration: str


class MockCardIssuer(CardIssuer):
    def __init__(self):
        self.mock_cards = {}

    def create_card(
        self,
        cardholder_id: str,
        purchase_amount: int,
        currency: str,
        merchant_id: str,
        allowed_categories: Optional[List[str]] = None,
        blocked_categories: Optional[List[str]] = None,
        expiration_seconds: int = 3600
    ) -> CardCreatedResponse:
        card_id = f"mock_card_{uuid.uuid4().hex[:8]}"
        last4 = str(random.randint(1000, 9999))
        card_number = f"4111 1111 1111 {last4}"
        cvv = str(random.randint(100, 999))
        expiration_time = datetime.now() + timedelta(seconds=expiration_seconds)
        expiration_str = expiration_time.isoformat()

        card_details = CardDetails(
            card_number=card_number,
            exp_date="12/25",
            cvv=cvv,
            name="Mock User",
            billing_address="123 Mock St, Mock City, Mock Country"
        )

        self.mock_cards[card_id] = card_details

        return CardCreatedResponse(
            id=card_id,
            cardholder=cardholder_id,
            last4=last4,
            purchase_limit=purchase_amount,
            currency=currency,
            merchant_id=merchant_id,
            usage="one-time",
            created=datetime.now().isoformat(),
            provider="mock",
            expiration=expiration_str
        )

    def get_card_details(self, card_id: str) -> CardDetails:
        if card_id not in self.mock_cards:
            raise ValueError(f"Card with ID {card_id} not found.")
        return self.mock_cards[card_id]
