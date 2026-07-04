from database import SessionLocal
from models import Company, Application, StatusHistory

db = SessionLocal()

# query all companies and print their names
companies = db.query(Company).all()
for company in companies:
    print(company.name)

applications = db.query(Application).all()
for app in applications:
    print(app.role_title, "-", app.company.name)

status_history = db.query(StatusHistory).all()
for h in status_history:
    print(h.status, "-", h.application.role_title)

db.close()