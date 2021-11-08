from sqlalchemy import Column, Integer, String, Boolean, create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from config import config

Base = declarative_base()
engine = create_engine('sqlite:///db/users.db', connect_args={"check_same_thread": False})
local_session = sessionmaker(autocommit=False, autoflush=False)

def get_session(engine: Engine) -> Session:
    local_session.configure(bind=engine)
    return local_session()

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    is_bot = Column(Boolean)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    language_code = Column(String)
    is_admin = Column(Boolean)


class Bans(Base):
    __tablename__ = "bans"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)

Base.metadata.create_all(bind=engine)

def duplicate_check(session, user_id, db):
    if session.query(db).filter(db.user_id == user_id).all():
        return False
    return True

def upload_to_users(session: Session, user):
    is_admin = True if user["id"] in config["ADMINS"] else False
    print(user)
    if duplicate_check(session=session, user_id=user["id"], db=Users):
        session.add(Users(user_id=user["id"],
                          is_bot=True if user["is_bot"] == "true" else False,
                          first_name=user["first_name"],
                          last_name=user["last_name"],
                          username=user["username"],
                          language_code=user["language_code"],
                          is_admin=is_admin
                          ))
        session.commit()
        session.close()
        return True
    else:
        session.commit()
        session.close()
        return False

def upload_to_bans(session: Session, user):
    if duplicate_check(session=session, user_id=user.user_id, db=Bans):
        session.add(Bans(user_id=user.user_id,
                          first_name=user.first_name,
                          last_name=user.last_name,
                          username=user.username,
                          ))
        session.commit()
        session.close()
        return True
    else:
        session.commit()
        session.close()
        return False


def remove_from_db(session: Session, db, user_id):
    for item in session.query(db).filter(db.user_id == user_id).all():
        session.delete(item)
    session.commit()
    session.close()