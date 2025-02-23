import uuid
import random
from datetime import datetime, timedelta
from typing import List, Optional
from .card_issuer import CardIssuer


class MockCardIssuer(CardIssuer):
    def create_card(
        self,
        cardholder_id: str,
        purchase_amount: int,
        currency: str,
        merchant_id: str,
        allowed_categories: Optional[List[str]] = None,
        blocked_categories: Optional[List[str]] = None,
        expiration_seconds: int = 3600
    ) -> dict:
        card_id = f"mock_card_{uuid.uuid4().hex[:8]}"
        last4 = str(random.randint(1000, 9999))
        # Calculate expiration time based on the provided expiration_seconds
        expiration_time = datetime.now() + timedelta(seconds=expiration_seconds)
        expiration_str = expiration_time.isoformat()
        return {
            "id": card_id,
            "cardholder": cardholder_id,
            "currency": currency,
            "purchase_limit": purchase_amount,
            "merchant_id": merchant_id,
            "last4": last4,
            "expiration": expiration_str,
            "usage": "one-time",
            "created": datetime.now().isoformat(),
            "provider": "mock"
        }
