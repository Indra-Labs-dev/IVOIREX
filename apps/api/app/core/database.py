import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
url=os.getenv('DATABASE_URL','sqlite:///./ivoirex.db').replace('postgresql://','postgresql+psycopg://')
engine=create_engine(url,pool_pre_ping=True)
SessionLocal=sessionmaker(engine,autoflush=False)
class Base(DeclarativeBase): pass
def session():
 db=SessionLocal()
 try: yield db
 finally: db.close()
