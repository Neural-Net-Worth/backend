from datetime import date
from pydantic import BaseModel, EmailStr


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
