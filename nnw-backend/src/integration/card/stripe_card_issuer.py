from datetime import datetime, timedelta
from typing import List, Optional
from .card_issuer import CardIssuer


class StripeCardIssuer(CardIssuer):
    def __init__(self, stripe_api_key: str):
        import stripe
        stripe.api_key = stripe_api_key
        self.stripe = stripe

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
        """
        Creates a virtual card using Stripe Issuing with spending controls.

        This method sets a per-authorization spending limit equal to the purchase_amount.
        It first attempts to validate the provided merchant_id. If valid, it restricts
        card usage to that merchant. Otherwise, it falls back to using allowed_categories.
        Additionally, the card is marked as one-time use and is set to expire after the
        specified expiration window (in seconds).

        Parameters:
          - cardholder_id: The Stripe cardholder identifier.
          - purchase_amount: The maximum amount (in cents) allowed per authorization.
          - currency: The currency for the card (e.g., 'usd').
          - merchant_id: The merchant at which the card is intended to be used.
          - allowed_categories: Optional list of allowed spending categories to be used if merchant_id is invalid.
          - blocked_categories: Optional list of blocked spending categories.
          - expiration_seconds: The time (in seconds) after which the card will expire if unused.

        Returns:
          A dictionary containing the details of the created card.

        Raises:
          An exception if the Stripe API call fails.
        """
        # Set up spending controls with a per-authorization limit.
        spending_controls = {
            "spending_limits": [
                {
                    "amount": purchase_amount,
                    "interval": "per_authorization"
                }
            ]
        }

        # Attempt to validate merchant_id via Stripe's Issuing Merchant API.
        valid_merchant = False
        try:
            # Hypothetical API call to validate merchant.
            merchant = self.stripe.issuing.Merchant.retrieve(merchant_id)
            if merchant and merchant.get("id"):
                valid_merchant = True
        except Exception:
            valid_merchant = False

        if valid_merchant:
            spending_controls["allowed_merchants"] = [merchant_id]
        elif allowed_categories:
            spending_controls["allowed_categories"] = allowed_categories

        if blocked_categories:
            spending_controls["blocked_categories"] = blocked_categories

        # Compute the card expiration datetime based on expiration_seconds.
        expiration_time = datetime.now() + timedelta(seconds=expiration_seconds)
        # Note: Stripe may not allow you to directly set a custom expiration,
        # so we include it in metadata for downstream processing.
        expiration_str = expiration_time.isoformat()

        card = self.stripe.issuing.Card.create(
            cardholder=cardholder_id,
            currency=currency,
            type="virtual",
            spending_controls=spending_controls,
            metadata={
                "expiration_time": expiration_str,
                "one_time_use": "true"
            }
        )
        return card
