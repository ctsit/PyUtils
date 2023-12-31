from deprecated import deprecated
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlmodel import Session, create_engine, SQLModel, select
from typing import List, Type, TypeVar

import logging
import os
import sqlite3


_T = TypeVar("_T", bound=SQLModel)


def convert_model_to_dict(model) -> dict:
    """Returns dictionary representation of the provided model

    Args:
        model (SQLModel): A model to convert to a dictionary

    Returns:
        dict
    """
    return {key: getattr(model, key) for key in model.__table__.columns.keys()}


class DbClient():
    def __init__(self, url: str, echo=False):
        """Creates a `DbClient`

        Args:
            url (str): The database url.
            echo (bool): Whether to print `sqlmodel` output to the console.

        Returns:
            An instance of DbClient connected to the database.

        Raises:
            Operational Error: When failing to connect to the database.
            Exception: When failing to create a `sqlmodel` engine.
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
        # self._sessionmaker = sessionmaker(bind=self._engine)

    @classmethod
    def mysql(cls, connection_string: str, echo=False):
        """Create a mysql DbClient.

        This is a wrapper around the constructor to simplify creating a mysql client.

        Args:
            connection_string (str): The db connection string i.e., `<user>:<password>@<host>:<port>/<database>`.
            echo (bool): Whether to print `sqlmodel` output to the console.
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
            echo (bool): Whether to print `sqlmodel` output to the console.

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

    def create_tables(self):
        """Creates the database tables

        `SQLModel`s need to be imported before calling this function. Refer to:
        https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#sqlmodel-metadata-order-matters

        Returns:
            None

        Raises:
            Exception: When failing to create tables in `sqlmodel` engine.
        """
        try:
            SQLModel.metadata.create_all(self._engine)
        except Exception as e:
            logging.error(f"Failed to create tables: {type(e)}")
            raise e

    def insert_data(self, model: _T) -> _T:
        """Insert model into database.

        Args:
            model (SQLModel): The model to insert into the database.

        Returns:
            The inserted entry.

        Raises:
            Exception: When failing to create a session to the `sqlmodel` engine.
        """
        # more information on setting expire_on_commit:
        # https://stackoverflow.com/questions/8253978/sqlalchemy-get-object-not-bound-to-a-session
        # https://groups.google.com/g/sqlalchemy/c/uYIawg4SUQQ?pli=1
        # In short, setting `expire_on_commit` to `False` allows accessing a field of the model after it has been
        # committed
        with Session(self._engine, expire_on_commit=False) as session:
            try:
                session.add(model)
                session.commit()
                logging.debug(f"Data inserted successfully for {model.__tablename__}")

                return model
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

    def query_model(self, model: Type[_T]) -> List[_T]:
        """Queries the database for the provided `model`.

        Args:
            model (Type[SQLModel]): The model class definition.

        Returns:
            list (List[SQLModel]): A list of all models.
        """
        models = []
        with Session(self._engine) as session:
            # Use SQLModel's inspect function to get the columns of the table
            # To return a dict instead:
            # mapper = inspect(model_class)
            # columns = [column.key for column in mapper.columns]
            # return [{column: getattr(result, column) for column in columns} for result in results]
            statement = select(model)
            results = session.exec(statement).unique()
            for entry in results:
                models.append(entry)

            return models

    @deprecated(version="2.1.1", reason="Use insert_data instead. This function will soon be removed")
    def update_model(self, model: _T, values: dict, pk_field: str = "id") -> _T:
        """Update model with values provided

        Args:
            model (Type[SQLModel]): The model class definition
            values (dict): A dictionary of the keys with updated values.
            pk_field (str): The primary key field of the provided model. Defaults to `id`.

        Returns:
            The updated entry.

        Raises:
            Exception: When failing to create a session to the `sqlmodel` engine.
        """
        with Session(self._engine) as session:
            try:
                object_to_update = session.get(type(model), getattr(model, pk_field))
                if object_to_update is not None:

                    # Update the object with the provided values
                    for key, value in values.items():
                        setattr(object_to_update, key, value)

                    session.commit()

                    return object_to_update

                raise Exception("The model does not exist.")
            except Exception as e:
                # Rollback the session in case of any other error
                session.rollback()
                logging.error(f"Error updating data: {str(e)}")
                raise e
