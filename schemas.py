from pydantic import BaseModel, EmailStr
import datetime
from typing import Optional

# contains API shape (what data is allowed to be sent to the API and what data is returned from the API)

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CompanyOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# incoming data from a user typing into a form
class ApplicationCreate(BaseModel):
    company_name: str
    role_title: str
    date_applied: datetime.date
    location: str
    application_link: Optional[str] = None
    current_status: str = "applied"

# outgoing data built from a real ORM object
class ApplicationOut(BaseModel):
    id: int
    company: CompanyOut
    role_title: str
    date_applied: datetime.date
    current_status: str
    location: str
    application_link: Optional[str] = None
    current_status: str = "applied"

    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: str
