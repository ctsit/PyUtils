from datetime import datetime
from py_utils.orm import DbClient
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func, Integer, String

import os
import unittest

Base = declarative_base()


class ImageInventory(Base):
    __tablename__ = 'image_inventory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=func.now())
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    core = Column(String)
    directory = Column(String)
    status = Column(String)
    image_type = Column(String)
    fs_mod_date = Column(DateTime)

    def validate(self):
        return (None and self.core is not None and self.status is not None
                and self.image_type is not None and self.fs_mod_date is not None)

    def __str__(self):
        return (
            f"core: {self.core}, directory: {self.directory}, status: {self.status},"
            f"image_type: {self.image_type}, fs_mod_date: {self.fs_mod_date}"
        )


class TestOrm(unittest.TestCase):
    def test_sqlite_crud_operations(self):
        sqlite_db = "test_db.db"
        db_client = DbClient.sqlite(sqlite_db)
        db_client.create_tables(Base, [ImageInventory])

        expected = 10

        for i in range(expected):
            data_to_insert = {
                "core": "bmc",
                "directory": os.getcwd(),
                "status": "new",
                "image_type": "mri",
                "fs_mod_date": datetime.now()
            }
            image = ImageInventory(**data_to_insert)
            db_client.insert_data(image)

        images = db_client.query_model(ImageInventory)
        actual = len(images)

        self.assertEqual(expected, actual)
        os.remove(sqlite_db)
