from db.db_manager import DBManager
from db.models import Base

db = DBManager()


def create_all():
    Base.metadata.create_all(db.engine)


if __name__ == '__main__':
    create_all()
