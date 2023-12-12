from datetime import datetime
from py_utils.orm import DbClient
from sqlmodel import Column, Enum, Field, Relationship, SQLModel
from typing import List, Optional

import os
import unittest


class ImageStatusTypes(str, Enum):
    new = "NEW"
    modified = "MODIFIED"
    failed_check = "FAILED_CHECKS"
    passed_check = "PASSED_CHECKS"
    uploaded_to_scan = "UPLOADED_TO_SCAN"
    uploaded_to_nacc = "UPLOADED_TO_NACC"
    uploaded_to_redcap = "UPLOADED_TO_REDCAP"


# class Image(DefaultModel):
class Image(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_date: datetime = Field(default=datetime.utcnow(), nullable=False)
    modified_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    core: str
    directory: str
    image_type: str
    fs_mod_date: datetime
    image_status: List["ImageStatus"] = Relationship(back_populates="image", sa_relationship_kwargs={"lazy": "joined"})

    def __str__(self):
        return (
            f"id: {self.id},"
            f"core: {self.core}, directory: {self.directory},"
            f"image_type: {self.image_type}, fs_mod_date: {self.fs_mod_date}"
        )

    def __eq__(self, other):
        return self.directory == other.directory


class ImageStatus(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_date: datetime = Field(default=datetime.utcnow(), nullable=False)
    modified_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    status: ImageStatusTypes = Field(sa_column=Column(Enum))
    image_id: Optional[int] = Field(default=None, foreign_key="image.id")
    image: Image = Relationship(back_populates="image_status")


class TestOrm(unittest.TestCase):
    def setUp(self) -> None:
        self.sqlite_db = "test_db.sqlite"
        self.db_client = DbClient.sqlite(self.sqlite_db)

        return super().setUp()

    def test_sqlite_crud_operations(self):
        self.db_client.create_tables()

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
        self.db_client.create_tables()

        expected_data = {
            "core": "dc",
            "directory": os.getcwd(),
            "image_type": "mri",
            "fs_mod_date": datetime.now()
        }

        # create a copy in memory to change against the entry returned from the db
        expected = Image(**expected_data)

        # create an image with bmc core
        created_image = self.db_client.insert_data(Image(**{
            "core": "bmc",
            "directory": os.getcwd(),
            "image_type": "mri",
            "fs_mod_date": datetime.now()
        }))
        # update the core
        created_image.core = expected_data.get("core", "")

        # apply the change to the database
        updated_image = self.db_client.insert_data(created_image)

        # assert that the updated image returned from the db client matches teh expected data
        self.assertEqual(expected.core, updated_image.core)

    def test_return_type_matches_model(self):
        self.db_client.create_tables()

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

    def tearDown(self) -> None:
        os.remove(self.sqlite_db)
        return super().tearDown()
