# PyUtils
PyUtils is a collection of utility python functions for use across CTS-IT python projects.

## Installation
### Necessary requirements
`PyCustodian` depends on [`poetry`](https://python-poetry.org). Follow the instructions on our [Wiki](https://wiki.ctsi.ufl.edu/books/python/page/how-to-install-poetry)

### Setup
1. Make sure you have Python 3 installed on your machine.
1. Clone or download the repository to your local machine:
    - `git clone git@github.com:ctsit/PyUtils.git`
1. Install the required dependencies by running the following command in the terminal:
    - `poetry install`

## Example Usage
```python
from datetime import datetime
from py_utils.orm import DbClient
from py_utils import utils
from sqlmodel import Field, SQLModel
from typing import Optional


class Image(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_date: datetime = Field(default=datetime.utcnow(), nullable=False)
    modified_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    core: str
    directory: str
    image_type: str


def main():
    db_client = DbClient.sqlite("test_db.db")
    db_client.create_tables()

    # create dummy data
    for i in range(10):
        data_to_insert = {
            core: f"title: ${i}",
            directory: "",
           image_type: "mri",
        }
        new_image = Image(**data_to_insert)
        db_client.insert_data(image)

    inserted_data = db_client.query_model(Image) # returns an `Image` class

    # optionally send email
    # utils.send_email()
```
