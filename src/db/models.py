from sqlalchemy import Column, BigInteger, String

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Photo(Base):
    __tablename__ = "photos"

    id = Column(BigInteger, primary_key=True)
    user_tg_id = Column(BigInteger, nullable=False)
    picsum_id = Column(BigInteger, nullable=False)
    author = Column(String, nullable=False)
    width = Column(BigInteger, nullable=False)
    height = Column(BigInteger, nullable=False)
    url = Column(String, nullable=False)
    download_url = Column(String, nullable=False)
