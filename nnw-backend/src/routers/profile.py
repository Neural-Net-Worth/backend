from pydantic import ValidationError
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import openai
from models import SessionLocal
from models.profile import Profile
from pydantic import BaseModel
from config import settings

router = APIRouter()


class BNPLRanking(BaseModel):
    rank: int
    provider: str
    highlight: str
    reasoning: str


class BNPLRankingsResponse(BaseModel):
    rankings: List[BNPLRanking]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Load OpenAI API Key
openai.api_key = settings.OPENAI_API_KEY


@router.get("/{user_id}", response_model=BNPLRankingsResponse)
def get_profile_with_ai_suggestion(user_id: int, product_price: float = Query(..., ge=0), db: Session = Depends(get_db)):
    # Fetch profile from the database
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Map profile data to the expected customer profile fields in the prompt
    customer_profile = {
        'name': profile.name,
        'age': profile.dob,
        'occupation': profile.job_title,
        'monthly_income': profile.monthly_income,
        'monthly_expenses': profile.monthly_expenses,
        'product_price': product_price,
    }

    bnpl_providers = """
    Klarna:
    - Cashback Program: Cashback is earned on qualifying purchases and credited to the Klarna balance.
    - Eligibility & Approval: Available only to customers residing in Ireland with a valid billing address.

    Affirm:
    - Eligibility: Users must be at least 18, reside in the UK, have a UK mobile number, and meet creditworthiness criteria.

    Clearpay:
    - Account & Eligibility: Available to UK residents aged 18+ with a valid UK mobile number and payment method.
    """

    prompt = f"""
        You are an expert AI assistant who evaluates and ranks BNPL (Buy Now, Pay Later) providers based on user financial details, provider terms, and approval likelihood. In this task, you must consider key details from the terms and conditions of different providers, including Klarna’s Cashback Program, Affirm’s lending practices, and Clearpay’s installment plan structure.

        ### User Details:
        - Age: {customer_profile['age']}
        - Occupation: {customer_profile['occupation']}
        - Monthly Income: ${customer_profile['monthly_income']}
        - Product Price: ${customer_profile['product_price']}

        ### BNPL Providers:
        {bnpl_providers}

        ### Provider Terms Highlights:

        **Klarna:**
        - **Cashback Program:** Cashback is earned on qualifying purchases (excluding taxes and fees) and credited to the Klarna balance (rounded down to the nearest cent).
        - **Eligibility & Approval:** Available only to customers residing in Ireland with a valid billing address; purchases require approval from participating stores.
        - **Terms Flexibility:** Cashback rates and eligibility may change, with limited liability under Irish law.
        - **Late Fees:** None mentioned explicitly.
        - **Repayment Flexibility:** No early repayment penalties mentioned.

        **Affirm:**
        - **Eligibility & User Requirements:** Users must be at least 18, reside in the UK, have a UK mobile number, and meet strict creditworthiness and affordability criteria.
        - **Service Model:** Affirm pays the merchant upfront while the user repays via a loan governed by a separate credit agreement.
        - **Data & Decision Making:** Uses personal data for identity verification, performs automated credit checks, and reports payment behavior to credit agencies.
        - **Liability & Updates:** Liability is limited, and terms can change with advance notice. Users are responsible for accurate account information and security.
        - **APR:** Typically ranges from 10% to 30% based on creditworthiness.
        - **Repayment Flexibility:** Potential for extension based on agreement terms.

        **Clearpay:**
        - **Account & Eligibility:** Available to UK residents (excluding Channel Islands), aged 18+ with a valid UK billing address, UK mobile number, and payment method.
        - **Plan Structure:** Provides a fixed 4-installment, interest-free plan with payments automatically deducted every two weeks after pre-authorization checks.
        - **Late Fees & Penalties:** Charges a £6 late fee for missed installments (with orders of £24 or more possibly incurring two fees capped at the lower of £24 or 25% of the purchase price).
        - **Refunds & Cancellations:** Adjusts payment schedules for refunds; orders may be canceled before delivery if issues arise.
        - **Security & Account Management:** Emphasizes secure account management, with measures to suspend or close accounts for suspicious activities.
        - **Late Fee Structure:** £6 for missed payments.

        #### Evaluation Criteria:
        1. **Approval Likelihood:** Can the user get approved based on their income, product price, and each provider's limits?
        2. **Interest Rate & Loan/Plan Terms:** Lower interest rates or favorable installment terms are preferred.
        3. **Repayment Options Match:** Does the provider offer the user’s preferred repayment method?
        4. **Financing Capacity:** Can the provider finance the purchase based on transaction and credit limits?
        5. **Clarity & Favorability of Terms:** Consider how clearly and favorably each provider presents its eligibility requirements, fees, and additional benefits (such as Klarna’s cashback, Affirm’s structured loan process, or Clearpay’s interest-free installment plan).

        #### Instructions:
        Rank the BNPL providers **from best to worst** using the evaluation criteria above. 

        Provide a ranked evaluation of BNPL (Buy Now, Pay Later) providers in the following strict JSON format:""" + """```json
        {
        "rankings": [
            {
            "rank": 1,
            "provider": "Provider A",
            "highlight": "0% Interest Rate!",
            "reasoning": "..."
            },
            {
            "rank": 2,
            "provider": "Provider B",
            "highlight": "High Approval Rate",
            "reasoning": "..."
            },
            {
            "rank": 3,
            "provider": "Provider C",
            "highlight": "Trusted by 90% of customers",
            "reasoning": "..."
            }
        ]
        }
        ```

        **Requirements:**
        1. Each ranking must include:
        - `"rank"`: An integer indicating the position (e.g., 1, 2, 3).
        - `"provider"`: The name of the BNPL provider.
        - `"highlight"`: A short, impactful highlight (e.g., "0% Interest Rate!", "High Approval Rate", "Trusted by 90% of customers").
        - `"reasoning"`: A summarized reasoning based on the evaluation criteria.
        
        2. The `"highlight"` field should include metrics or quantitative impact wherever possible.

        3. Please respond with the JSON as plain text, without any formatting, code blocks, or additional commentary.
    """

    # Call OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a financial advisor that evaluates BNPL (Buy Now, Pay Later) options for users."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )
        ai_suggestion = response["choices"][0]["message"]["content"]

        # Parse the LLM response into the Pydantic model
        try:
            bnpl_rankings = BNPLRankingsResponse.model_validate_json(
                ai_suggestion)
        except ValidationError as ve:
            raise HTTPException(
                status_code=500, detail=f"Validation Error: {ve}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")

    return bnpl_rankings
