from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from schemas import UserCreate, UserOut
from auth import hash_password
from auth import hash_password, verify_password, create_access_token
from schemas import UserLogin
from auth import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from schemas import ApplicationCreate, ApplicationOut, StatusUpdate
from models import Application, Company, StatusHistory
from fastapi.middleware.cors import CORSMiddleware

# create FastAPI instance and the get_db() function to create a new database session for each request
# auth.py tools used here to hash passwords, verify passwords, create JWT tokens, and get the current user from a token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "https://wondrous-syrniki-efd098.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup", response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)): 
    # check if user already exists in database
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # hash user password using hash_password()
    hashed_password = hash_password(user.password)
    # create new_user object with email and hashed password
    new_user = User(email=user.email, password_hash=hashed_password)

    # add new_user to session, commit, and refresh
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # look up user by their email
    current_user = db.query(User).filter(User.email == credentials.email).first()
    
    # if user not found in database, return 401 error
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # check if password matches using verify_password()
    check_password = verify_password(credentials.password, current_user.password_hash)
    # raise 401 error if password doesn't match
    if not check_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # create access token and return it since passwords match and user was found
    else:
        token = create_access_token({"sub": str(current_user.id)})
        return {"access_token": token, "token_type": "bearer"}
    
@app.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

# allows users to add new applications to the database, creating a new company if it doesn't already exist, 
# and linking the application to the current user
@app.post("/applications", response_model=ApplicationOut)
def create_application(application: ApplicationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # normalize company name to title case
    normalized_name = application.company_name.title()

    # check if company already exists in database
    company = db.query(Company).filter(Company.name == normalized_name).first()
    # if company doesn't exist, create a new company
    if not company:
        company = Company(name=normalized_name)
        db.add(company)
        db.commit()
        db.refresh(company)

    # create new application object with the company_id, role_title, date_applied, and user_id
    new_application = Application(
        company_id=company.id,
        role_title=application.role_title,
        date_applied=application.date_applied,
        user_id=current_user.id,
        location=application.location,
        application_link=application.application_link,
        current_status=application.current_status
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application

@app.get("/applications", response_model=list[ApplicationOut])
def read_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    applications = db.query(Application).filter(Application.user_id == current_user.id).all()
    return applications

@app.patch("/applications/{id}/status", response_model=ApplicationOut)
def update_application_status(id: int, status_update: StatusUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == id, Application.user_id == current_user.id).first()
    # raise on exception if application not found
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.current_status = status_update.status
    # update the status history table with the new status along with updating the status of the application
    update_status_history = StatusHistory(application_id=application.id, status=status_update.status)

    db.add(update_status_history)
    db.commit()
    db.refresh(application)
    return application
