from database import engine, Base
from models import Company, Application, StatusHistory, User

# creates the tables in the database based on the models defined in models.py

Base.metadata.create_all(bind=engine)
print("Tables created.")