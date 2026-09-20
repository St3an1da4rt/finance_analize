from enum import Enum

from pydantic import BaseModel, Field

class FinReportCreate:
    title: str = Field(max_length=100)
    amount: int = Field(min=100, max_length=10000000)
    # is_income: boo
    class_flow: str = Field(max_length=100)

# class FinReportUpdate:
