from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from tests.utils.model_test_utils import save_object


class SampleModelCustomConstraint(Base):
    """Sample model for testing custom constraint."""
    name = Column(String(20), nullable=False, unique=True)


class TestCustomConstraintApplication:
    pass


class TestCustomConstraintDatabase:
    pass
