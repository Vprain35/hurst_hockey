from sqlmodel import Session, select
from models import Bio, Stats, engine
from sqlalchemy import func
import pandas as pd

with Session(engine) as session:
    statement = (
        select(Bio)
    )
    records = session.exec(statement).all()

records_list = []
for record in records:
    records_list.append(record.model_dump())

records_df = pd.DataFrame(records_list)
print(records_df)