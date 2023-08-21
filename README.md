# PyUtils
PyUtils is a collection of utility python functions for use across CTS-IT python projects.

# Example Usage
```python
from py_utils.orm import DbClient
from py_utils import utils
from sqlalchemy import Column, DateTime, func, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = delcarative_base()

class DataClass(Base):
    __tablename__ = "invalid_data_class"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=func.now())
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    title = Column(String)


def main():
    db_client = DbClient.sqlite("test_db.db")
    db_client.create_tables(Base, [DataClass])

    # create dummy data
    for i in range(10):
        data_to_insert = {
            title: f"title: ${i}"
        }
        new_data_class = DataClass(**data_to_insert)
        db_client.insert_data(new_data_class)

    inserted_data = db_client.query_model(DataClass)

    # optionally send email
    # utils.send_email()
```
