from sqlmodel import Session, select
from models import Bio, Stats, engine
from sqlalchemy import func
import pandas as pd

with Session(engine) as session:
    statement = (
        select(Bio.position,func.avg(Bio.weight))
        .group_by(Bio.position)
        .having(func.avg(Bio.weight)>180)
    )
    records = session.exec(statement).all()

records_df = pd.DataFrame(records)

print(records_df)