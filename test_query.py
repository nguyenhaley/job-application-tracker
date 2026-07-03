from database import SessionLocal
from models import Company, Application, StatusHistory

db = SessionLocal()

# YOUR CODE HERE — query all companies and print their names

db.close()