#from sqlalchemy import create_engine
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import sessionmaker
#from .config import settings

# The 'check_same_thread' is needed only for SQLite
#engine = create_engine(
 #   settings.DATABASE_URL, connect_args={"check_same_thread": False}
#)
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base = declarative_base()

# Dependency for FastAPI to get a database session per request
#def get_db():
 #   db = SessionLocal()
  #  try:
   #     yield db
    #finally:
     #   db.close()
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# --- MODIFIED: We now use the DATABASE_URL property from settings ---
#
#    !!! CRITICAL FIX !!!
#
#    We MUST remove: connect_args={"check_same_thread": False}
#    That argument is for SQLite ONLY.
#
# --- END MODIFIED ---

engine = create_engine(
    settings.DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI to get a database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()