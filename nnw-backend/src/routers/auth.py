import uuid
import hashlib
import jwt

from pydantic import BaseModel, EmailStr
from datetime import datetime, date, timedelta
from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models import SessionLocal
from models.user import User
from models.profile import Profile
from models.cardholder import Cardholder

from integration.card_issuer.cardholder import CardholderIssuer
from integration.card_issuer.mock_cardholder import MockCardholderIssuer
from integration.card_issuer.stripe_cardholder import StripeCardholderIssuer

from config import settings

router = APIRouter()

# Configuration
JWT_SECRET = settings.JWT_SECRET
STRIPE_API_KEY = settings.STRIPE_API_KEY
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    name: str
    mobile: str
    dob: date
    address: str
    job_title: str
    monthly_income: float
    monthly_expenses: float

# Dependency: DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


# def create_refresh_token(user_id: int):
#     jti = str(uuid.uuid4())
#     expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
#     payload = {"user_id": user_id, "jti": jti, "exp": expire}
#     token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
#     return token, jti, expire


def hash_jti(jti: str) -> str:
    return hashlib.sha256(jti.encode()).hexdigest()


def get_cardholder_issuer() -> CardholderIssuer:
    if settings.ENV == "production":
        return StripeCardholderIssuer(STRIPE_API_KEY)
    return MockCardholderIssuer()


@router.post("/register")
def register(reg_data: UserRegistration, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == reg_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create the user record
    hashed_pw = get_password_hash(reg_data.password)
    new_user = User(email=reg_data.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create the profile record referencing the new user
    profile = Profile(
        user_id=new_user.id,
        name=reg_data.name,
        mobile=reg_data.mobile,
        dob=reg_data.dob,
        address=reg_data.address,
        job_title=reg_data.job_title,
        monthly_income=reg_data.monthly_income,
        monthly_expenses=reg_data.monthly_expenses
    )
    db.add(profile)
    db.commit()
    # Create a cardholder using the Stripe integration
    try:
        cardholder_service = get_cardholder_issuer()
        cardholder_data = cardholder_service.create_cardholder(
            name=reg_data.name,
            email=reg_data.email,
            phone_number=reg_data.mobile,
            address=reg_data.address
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating cardholder: {str(e)}")

    # Persist the cardholder information in our new table
    new_cardholder = Cardholder(
        user_id=new_user.id,
        cardholder_id=cardholder_data["id"],
        provider="stripe",
    )
    db.add(new_cardholder)
    db.commit()

    return {"message": "User registered with profile and cardholder", "user_id": new_user.id}


# @router.post("/login", response_model=TokenResponse)
# def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = db.query(UserRegistration).filter(
#         UserRegistration.email == form_data.username).first()
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token_data = {"user_id": user.id}
#     access_token = create_access_token(token_data)

#     refresh_token, jti, expires = create_refresh_token(user.id)
#     token_record = RefreshToken(jti_hash=hash_jti(
#         jti), user_id=user.id, expires=expires)
#     db.add(token_record)
#     db.commit()

#     return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# @router.post("/refresh", response_model=TokenResponse)
# def refresh(refresh_token: str = Body(...), db: Session = Depends(get_db)):
#     try:
#         payload = jwt.decode(refresh_token, JWT_SECRET,
#                              algorithms=[JWT_ALGORITHM])
#         user_id = payload.get("user_id")
#         jti = payload.get("jti")
#         if not user_id or not jti:
#             raise HTTPException(
#                 status_code=401, detail="Invalid token payload")
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Refresh token expired")
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=401, detail="Invalid refresh token")

#     token_hash_val = hash_jti(jti)
#     token_record = db.query(RefreshToken).filter(
#         RefreshToken.user_id == user_id,
#         RefreshToken.jti_hash == token_hash_val
#     ).first()

#     if not token_record:
#         raise HTTPException(
#             status_code=401, detail="Refresh token not recognized")
#     if token_record.expires < datetime.utcnow():
#         db.delete(token_record)
#         db.commit()
#         raise HTTPException(status_code=401, detail="Refresh token expired")

#     # Rotate refresh token: delete old token record.
#     db.delete(token_record)
#     db.commit()

#     token_data = {"user_id": user_id}
#     new_access_token = create_access_token(token_data)
#     new_refresh_token, new_jti, new_expires = create_refresh_token(user_id)
#     new_token_record = RefreshToken(jti_hash=hash_jti(
#         new_jti), user_id=user_id, expires=new_expires)
#     db.add(new_token_record)
#     db.commit()

#     return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)
