from database import engine, Base
from models import Company, Application, StatusHistory, User

Base.metadata.create_all(bind=engine)
print("Tables created.")