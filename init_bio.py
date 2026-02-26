from sqlmodel import Session
from bio_instances import get_bio_instances
from models import Bio, engine


with Session(engine) as session:
    existing_bios = session.query(Bio).all()
    if not existing_bios:
        for bio in get_bio_instances():
            session.add(bio)
        session.commit()

