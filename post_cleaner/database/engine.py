import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


POSTGRES_USER = os.getenv('POSTGRES_USER', 'pastebin')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'pastebin')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'pastebin')

engine = create_engine(f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')

Session = sessionmaker(bind=engine)
