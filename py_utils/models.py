from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel
from typing import Optional


class JobStatusLevels(str, Enum):
    INFO = "INFO"
    DEBUG = "DEBUG"
    ERROR = "ERROR"


class JobStatus(SQLModel, table=True):
    __tablename__: str = "job_status"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_date: datetime = Field(default=datetime.utcnow(), nullable=False)
    modified_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    host: str = Field(nullable=True)
    script_path: str = Field(nullable=True)
    script_name: str = Field(nullable=True)
    executed_by: str = Field(nullable=True)
    script_start_time: datetime = Field(nullable=True)
    script_end_time: datetime = Field(nullable=True)
    elapsed_time: int = Field(nullable=True)
    job_summary_data: str = Field(nullable=True, max_length=15000)
    level: JobStatusLevels = Field(nullable=True)

    def __str__(self):
        return (
            f"script_name: {self.script_name}, executed by: {self.executed_by}"
            f" level: {self.level},"
            f" job_summary_data: {self.job_summary_data},"
            f" start_time: {self.script_start_time}, end_time: {self.script_end_time},"
            f" elapsed_time: {self.elapsed_time}"
        )
