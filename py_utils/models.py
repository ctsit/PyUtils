from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel
from typing import Optional, List
from sqlmodel import Relationship
from datetime import timezone


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
    report_data: List["ReportData"] = Relationship(
        back_populates="job_status", sa_relationship_kwargs={"lazy": "joined"})

    def __str__(self):
        return (
            f"script_name: {self.script_name}, executed by: {self.executed_by}"
            f" level: {self.level},"
            f" job_summary_data: {self.job_summary_data},"
            f" start_time: {self.script_start_time}, end_time: {self.script_end_time},"
            f" elapsed_time: {self.elapsed_time}"
        )


class ReportData(SQLModel, table=True):
    __tablename__: str = "report_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    report_data: Optional[str] = Field(default='', max_length=16000)
    report_name: Optional[str] = Field(default='')
    date_generated: datetime = Field(default=datetime.now(timezone.utc), nullable=False)
    script_name: Optional[str] = Field()
    report_size: Optional[int] = Field(default=0)
    job_status_id: Optional[int] = Field(default=None, foreign_key="job_status.id")
    job_status: JobStatus = Relationship(back_populates="report_data")

    def __str__(self):
        return (
            f"id: {self.id},"
            f"report_data: {self.report_data}, report_name: {self.report_name},"
            f"date_generated: {self.date_generated}, script_name: {self.script_name}"
        )

    def __eq__(self, other):
        return self.id == other.id and self.report_data == other.report_data and \
            self.report_name == other.report_name and self.date_generated == other.date_generated and \
            self.script_name == other.script_name and self.job_status_id == other.job_status_id

    def __hash__(self):
        return hash((self.id, self.report_data, self.report_name, self.date_generated, self.script_name,
                     self.job_status_id))
