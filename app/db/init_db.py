from app.db.base import Base
from app.db.session import engine

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized!")

if __name__ == "__main__":
    init_db()
