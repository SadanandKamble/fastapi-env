from database import DATABASE_URL
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker

# postgresSQL conection string
DATABASE_URL = "postgresql://user:Sada0001@localhost:5432/studentdb" 
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker( bind=engine)

stuents = sqlalchemy.Table(
    "students", 
    sqlalchemy.MetaData(),
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("score", sqlalchemy.Float),
)
 

