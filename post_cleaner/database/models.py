from sqlalchemy import Table, MetaData
from sqlalchemy.ext.declarative import declarative_base

from .engine import engine

Base = declarative_base()

metadata = MetaData()
metadata.reflect(bind=engine)


UserTable = Table('auth_user', metadata, autoload_with=engine)

PasteTable = Table('post_bin_paste', metadata, autoload_with=engine)

class Paste(Base):
    __table__ = PasteTable

    @property
    def user(self):
        return self.user_id

    def __str__(self):
        return f'<Paste: {self.id}>'