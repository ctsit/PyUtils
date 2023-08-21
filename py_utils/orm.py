from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import sessionmaker

import logging
import os
import sqlite3


class DbClient():
    def __init__(self, driver: str, url: str, echo=False):
        try:
            connection_string = f"{driver}:///{url}"
            logging.info(f"orm.py: Attempting to connect to: {url}")

            self._engine = create_engine(connection_string, echo=echo)
            self._engine.connect()
        except OperationalError as e:
            logging.error(f"orm.py: Connection failed: {e}")
            raise e
        except Exception as e:
            logging.error(f"orm.py: Failed to create engine with error of type: {type(e)}")
            raise e
        self._sessionmaker = sessionmaker(bind=self._engine)

    @classmethod
    def sqlite(cls, path: str, echo=False):
        try:
            # check if the file exists
            if not os.path.exists(path):
                # connect to create a new sqlite db
                conn = sqlite3.connect(path)
                conn.close()
        except Exception as e:
            logging.error(
                "orm.py: Failed to create sqlite db. Double check that the path is correct.")
            raise e

        return cls("sqlite", path, echo)

    def create_tables(self, base, models: list):
        """
        """
        try:
            inspector = inspect(self._engine)
        except Exception as e:
            logging.error(f"orm.py: Failed to inspect engine with error of type: {type(e)}")
            raise e

        for model in models:
            if not inspector.has_table(model.__tablename__):
                base.metadata.create_all(self._engine)
                logging.info(f"orm.py: Creating table: {model.__tablename__}")
            else:
                logging.info(f"orm.py: Table already exists: {model.__tablename__}")

    def insert_data(self, model):
        try:
            session = self._sessionmaker()
        except Exception as e:
            logging.error(f"form.py: Failed to create session with error of type: {type(e)}")
            raise e

        session.add(model)

        try:
            # Validate the model instance
            model.validate()

            # Commit the session to persist the changes
            session.commit()
            logging.info("orm.py: Data inserted successfully!")
        except IntegrityError as e:
            # Rollback the session in case of any integrity error
            session.rollback()
            logging.error(f"orm.py: Integrity Error: {str(e)}")
        except Exception as e:
            # Rollback the session in case of any other error
            session.rollback()
            logging.error(f"orm.py: Error inserting data: {str(e)}")
        finally:
            # Close the session
            session.close()

    def query_model(self, model_class) -> list:
        """
        """
        session = self._sessionmaker()

        # Use SQLAlchemy's inspect function to get the columns of the table
        mapper = inspect(model_class)
        columns = [column.key for column in mapper.columns]

        # Execute the query and return the results
        results = session.query(model_class).all()
        return [{column: getattr(result, column) for column in columns} for result in results]
