from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import sessionmaker

import logging
import os
import sqlite3


class DbClient():
    def __init__(self, driver: str, url: str, echo=False):
        """Creates a `DbClient`

        Args:
            driver (str): The driver to use for the database connection i.e., `sqlite`.
            url (str): The database url.
            echo (bool): Whether to print `sqlalchemy` output to the console.

        Returns:
            An instance of DbClient connected to the database.

        Raises:
            Operational Error: When failing to connect to the database.
            Exception: When failing to create a `sqlalchemy` engine.
        """
        try:
            connection_string = f"{driver}:///{url}"
            logging.info(f"Attempting to connect to: {url}")

            self._engine = create_engine(connection_string, echo=echo)
            self._engine.connect()
            logging.info(f"Successfully connected to: {url}")
        except OperationalError as e:
            logging.error(f"Connection failed: {e}")
            raise e
        except Exception as e:
            logging.error(f"Failed to create engine with error of type: {type(e)}")
            raise e
        self._sessionmaker = sessionmaker(bind=self._engine)

    @classmethod
    def sqlite(cls, path: str, echo=False):
        """Create a sqlite DbClient.

        This is a wrapper around the constructor to simplify creating a sqlite client,
        creating the sqlite db if it does not already exist.

        Args:
            path (str): The path to the sqlite db.
            echo (bool): Whether to print `sqlalchemy` output to the console.

        Returns:
            An instance of DbClient connected to a sqlite database.

        Raises:
            Exception: When failing to create a new sqlite database.
        """
        try:
            # check if the file exists
            if not os.path.exists(path):
                # connect to create a new sqlite db
                conn = sqlite3.connect(path)
                conn.close()
        except Exception as e:
            logging.error(
                "Failed to create sqlite db. Double check that the path is correct.")
            raise e

        return cls("sqlite", path, echo)

    def create_tables(self, base, models: list):
        """Creates the database tables

        The base is passed in to decouple model definition from this package. This way models can
        be defined locally in a separate package rather than in this utility package.

        Args:
            base (`sqlalchemy.ext.declarative:declarative_base`): An instance of `declarative_base`
            used to define `sqlalchemy` data models. See `test_orm.py` for an example data class
            definition.
            models (list): A list of `sqlalchemy` data tables.

        Returns:
            None

        Raises:
            Exception: When failing to inspect the `sqlalchemy` engine.
        """
        try:
            inspector = inspect(self._engine)
        except Exception as e:
            logging.error(f"Failed to inspect engine with error of type: {type(e)}")
            raise e

        for model in models:
            if not inspector.has_table(model.__tablename__):
                base.metadata.create_all(self._engine)
                logging.info(f"Creating table: {model.__tablename__}")
            else:
                logging.info(f"Table already exists: {model.__tablename__}")

    def insert_data(self, model):
        """Insert model data into database.

        The model is expected to have a `validate` function defined. See `test_orm.py` for an
        example validate function.

        Args:
            model: A `sqlalchemy` data table class.

        Returns:
            None

        Raises:
            Exception: When failing to create a session to the `sqlalchemy` engine.
        """
        try:
            session = self._sessionmaker()
        except Exception as e:
            logging.error(f"fFailed to create session with error of type: {type(e)}")
            raise e

        session.add(model)

        try:
            is_valid = model.validate()

            if not is_valid:
                raise Exception(f"Model failed validation: {model}")

            session.commit()
            logging.info(f"Data inserted successfully for {model.__tablename__}")
        except AttributeError as e:
            session.rollback()
            logging.error(
                f"Attribute Error: {str(e)}. Verify that a `validate` has been defined as "
                f"part of the data class")
            raise e
        except IntegrityError as e:
            # Rollback the session in case of any integrity error
            session.rollback()
            logging.error(f"Integrity Error: {str(e)}")
            raise e
        except Exception as e:
            # Rollback the session in case of any other error
            session.rollback()
            logging.error(f"Error inserting data: {str(e)}")
            raise e
        finally:
            # Close the session
            session.close()

    def query_model(self, model_class) -> list:
        """Queries the database for the provided `model_class`.

        Args:
            model_class: The `sqlalchemy` data class to query the database for.

        Returns:
            list: A list of the `model_class`.
        """
        session = self._sessionmaker()

        # Use SQLAlchemy's inspect function to get the columns of the table
        mapper = inspect(model_class)
        columns = [column.key for column in mapper.columns]

        # Execute the query and return the results
        results = session.query(model_class).all()
        return [{column: getattr(result, column) for column in columns} for result in results]
