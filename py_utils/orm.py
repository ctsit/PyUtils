from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import sessionmaker

import logging
import os
import sqlite3


class DbClient():
    def __init__(self, url: str, echo=False):
        """Creates a `DbClient`

        Args:
            url (str): The database url.
            echo (bool): Whether to print `sqlalchemy` output to the console.

        Returns:
            An instance of DbClient connected to the database.

        Raises:
            Operational Error: When failing to connect to the database.
            Exception: When failing to create a `sqlalchemy` engine.
        """
        try:
            logging.debug(f"Attempting to connect to: {url}")

            self._engine = create_engine(url, echo=echo)
            self._engine.connect()
            logging.debug("Successfully connected to db.")
        except OperationalError as e:
            logging.error(f"Connection failed: {e}")
            raise e
        except Exception as e:
            logging.error(f"Failed to create engine with error of type: {type(e)}")
            raise e
        self._sessionmaker = sessionmaker(bind=self._engine)

    @classmethod
    def mysql(cls, connection_string: str, echo=False):
        """Create a mysql DbClient.

        This is a wrapper around the constructor to simplify creating a mysql client.

        Args:
            connection_string (str): The db connection string i.e., `<user>:<password>@<host>:<port>/<database>`.
            echo (bool): Whether to print `sqlalchemy` output to the console.
        """
        url = f"mysql://{connection_string}"
        return cls(url, echo)

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

        url = f"sqlite:///{path}"
        return cls(url, echo)

    def _convert_model_to_dict(self, model) -> dict:
        """Returns dictionary representation of the provided model

        Args:
            model: A `sqlalchemy` data class

        Returns:
            dict
        """
        return {key: getattr(model, key) for key in model.__table__.columns.keys()}

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
                logging.debug(f"Creating table: {model.__tablename__}")
            else:
                logging.debug(f"Table already exists: {model.__tablename__}")

    def insert_data(self, model) -> dict:
        """Insert model data into database.

        The model is expected to have a `validate` function defined. See `test_orm.py` for an
        example validate function.

        Args:
            model: A `sqlalchemy` data table class.

        Returns:
            dict

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
            logging.debug(f"Data inserted successfully for {model.__tablename__}")

            return self._convert_model_to_dict(model)
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
        # To return a dict instead:
        # mapper = inspect(model_class)
        # columns = [column.key for column in mapper.columns]
        # return [{column: getattr(result, column) for column in columns} for result in results]

        # Execute the query and return the results
        return session.query(model_class).all()

    def update_model(self, model_class, id, **kwargs) -> dict:
        """Update model with kwargs provided

        Args:
            model: A `sqlalchemy` data table class.

        Returns:
            dict

        Raises:
            Exception: When failing to create a session to the `sqlalchemy` engine.
        """
        try:
            session = self._sessionmaker()
        except Exception as e:
            logging.error(f"fFailed to create session with error of type: {type(e)}")
            raise e

        try:
            # Retrieve the object that you want to update
            object_to_update = session.query(model_class).get(id)

            # Update the object with the provided values
            for key, value in kwargs.items():
                setattr(object_to_update, key, value)

            session.commit()

            return self._convert_model_to_dict(object_to_update)
        except Exception as e:
            # Rollback the session in case of any other error
            session.rollback()
            logging.error(f"Error inserting data: {str(e)}")
            raise e
        finally:
            # Close the session
            session.close()
