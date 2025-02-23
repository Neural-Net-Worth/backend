from abc import ABC, abstractmethod
from typing import List, Optional


class CardIssuer(ABC):
    @abstractmethod
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
        Create a one-time disposable card limited to the purchase amount and restricted by spending controls.

        The implementation should attempt to validate the provided merchant_id with the underlying
        card issuing service. If the merchant_id is valid, the card’s spending controls will restrict usage 
        to that merchant. Otherwise, the allowed_categories (if provided) will be applied as a fallback.

        The card is intended for one-time use only and will expire after the specified expiration window (in seconds)
        or be canceled automatically once used.

        Parameters:
          - cardholder_id: The identifier for the cardholder.
          - purchase_amount: The maximum amount (in cents) allowed per authorization.
          - currency: The currency code (e.g., 'usd').
          - merchant_id: The merchant at which the card is intended to be used.
          - allowed_categories: Optional list of allowed spending categories (used as fallback if merchant_id is invalid).
          - blocked_categories: Optional list of blocked spending categories.
          - expiration_seconds: The time (in seconds) after which the card will expire if unused (default: 3600 seconds).

        Returns:
          A dictionary representing the card details.

        Raises:
          An exception if the card creation fails.
        """
        pass
