from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg://app:app@localhost:5432/users"

engine = create_engine(DATABASE_URL)