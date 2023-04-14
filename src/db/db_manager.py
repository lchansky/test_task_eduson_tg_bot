import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import count

from config import ENV_FILE_PATH
from db.models import Photo


load_dotenv(ENV_FILE_PATH)


class DBManager:
    def __init__(self):
        self.__connection = f'postgresql+psycopg2://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}' \
                            f'@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}'
        self.engine = create_engine(self.__connection)

    def add_photos(self, user_tg_id: int, photos: list[dict]):
        photos_objects = [
            Photo(
                user_tg_id=user_tg_id,
                picsum_id=photo.get('id'),
                author=photo.get('author'),
                width=photo.get('width'),
                height=photo.get('height'),
                url=photo.get('url'),
                download_url=photo.get('download_url'),
            )
            for photo in photos
        ]
        with Session(self.engine) as session:
            session.bulk_save_objects(photos_objects)
            session.commit()

    def get_photos_count(self, user_tg_id: int) -> int:
        with Session(self.engine) as session:
            result = session.query(Photo).filter(Photo.user_tg_id == user_tg_id).count()
            return result

    def get_photos(self, user_tg_id: int, offset: int = None, limit: int = None) -> list[Photo]:
        with Session(self.engine) as session:
            query = select(Photo).where(Photo.user_tg_id == user_tg_id)
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            photos = session.scalars(query)
            return list(photos)

    def get_photo(self, photo_id: int):
        with Session(self.engine) as session:
            query = select(Photo).where(Photo.id == photo_id)
            return session.scalar(query)

    def delete_photo(self, photo_id: int):
        with Session(self.engine) as session:
            advertisement = session.query(Photo).filter_by(id=photo_id).first()
            session.delete(advertisement)
            session.commit()
