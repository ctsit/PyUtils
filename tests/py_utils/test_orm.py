from datetime import datetime
from py_utils.orm import DbClient
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, DateTime, Enum, func, ForeignKey, Integer, String

import enum
import os
import unittest

Base = declarative_base()


class InvalidDataClass(Base):
    __tablename__ = "invalid_data_class"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=func.now())
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    title = Column(String)


class ImageStatusTypes(enum.Enum):
    new = "NEW"
    modified = "MODIFIED"
    failed_check = "FAILED_CHECKS"
    passed_check = "PASSED_CHECKS"
    uploaded_to_scan = "UPLOADED_TO_SCAN"
    uploaded_to_nacc = "UPLOADED_TO_NACC"
    uploaded_to_redcap = "UPLOADED_TO_REDCAP"


class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=func.now())
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    core = Column(String)
    directory = Column(String)
    image_type = Column(String)
    fs_mod_date = Column(DateTime)
    image_status = relationship("ImageStatus", back_populates="image")

    def validate(self):
        if self.core is not None \
                and self.image_type is not None \
                and self.fs_mod_date is not None:
            return True

        return False

    def __str__(self):
        return (
            f"id: {self.id},"
            f"core: {self.core}, directory: {self.directory},"
            f"image_type: {self.image_type}, fs_mod_date: {self.fs_mod_date}"
        )

    def __eq__(self, other):
        return self.directory == other.directory


class ImageStatus(Base):
    __tablename__ = 'image_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column(DateTime, default=func.now())
    modified_date = Column(DateTime, default=func.now(), onupdate=func.now())
    status = Column(Enum(ImageStatusTypes))
    image_id = Column(Integer, ForeignKey("image.id"))
    image = relationship("Image", back_populates="image_status")

    def validate(self):
        return self.status in ImageStatusTypes


class TestOrm(unittest.TestCase):
    def setUp(self) -> None:
        self.sqlite_db = "test_db.sqlite"
        self.db_client = DbClient.sqlite(self.sqlite_db)

        return super().setUp()

    def test_sqlite_crud_operations(self):
        self.db_client.create_tables(Base, [Image])

        expected = 10

        for i in range(expected):
            data_to_insert = {
                "core": "bmc",
                "directory": os.getcwd(),
                "image_type": "mri",
                "fs_mod_date": datetime.now()
            }
            image = Image(**data_to_insert)
            self.db_client.insert_data(image)

        images = self.db_client.query_model(Image)
        actual = len(images)

        self.assertEqual(expected, actual)

    def test_update_model(self):
        self.db_client.create_tables(Base, [Image])

        original_data = {
            "core": "bmc",
            "directory": os.getcwd(),
            "image_type": "mri",
            "fs_mod_date": datetime.now()
        }
        image = Image(**original_data)

        updated_data = {
            "core": "dc",
            "directory": os.getcwd(),
            "image_type": "mri",
            "fs_mod_date": datetime.now()
        }
        actual = Image(**updated_data)

        created_image = self.db_client.insert_data(image)
        self.db_client.update_model(Image, created_image["id"], **{"core": "dc"})

        expected = self.db_client.query_model(Image)[0]

        self.assertEqual(actual, expected)

    def test_return_type_matches_model(self):
        self.db_client.create_tables(Base, [Image])

        data_to_insert = {
            "core": "bmc",
            "directory": os.getcwd(),
            "image_type": "mri",
            "fs_mod_date": datetime.now()
        }
        image = Image(**data_to_insert)
        self.db_client.insert_data(image)

        actual = type([image])
        expected = self.db_client.query_model(Image)

        self.assertIsInstance(expected, actual)

    def test_invalid_data_class(self):
        sqlite_db = "test_db.db"
        db_client = DbClient.sqlite(sqlite_db)
        db_client.create_tables(Base, [InvalidDataClass])

        data_to_insert = {
            "title": "test title"
        }
        invalid_data_class = InvalidDataClass(**data_to_insert)

        try:
            db_client.insert_data(invalid_data_class)
        except AttributeError as actual:
            self.assertIsInstance(actual, AttributeError)
            return

        assert False

    def tearDown(self) -> None:
        os.remove(self.sqlite_db)
        return super().tearDown()
