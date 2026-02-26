from sqlmodel import Session
from stats_instances import get_stats_instances
from models import engine, Stats


with Session(engine) as session:
    existing_stats = session.query(Stats).all()
    if not existing_stats:
        for stat in get_stats_instances():
            session.add(stat)
        session.commit()

