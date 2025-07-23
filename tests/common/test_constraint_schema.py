from decimal import Decimal
from typing import List

import pytest
from pydantic import BaseModel, Field, StrictInt, StrictStr, ValidationError


class ConstraintTestSchema(BaseModel):
    """
    Test schema demonstrating various constraint metadata types.

    This schema includes common constraints that are frequently used
    in production applications and should be thoroughly tested.
    """

    # String constraints
    username: StrictStr = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r'^[a-zA-Z0-9_]+$',
        description="Username with alphanumeric and underscore only"
    )

    score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Score must be greater than 0 and at most 100"
    )

    age: int = Field(
        ...,
        gt=0,
        lt=150,
        description="Age must be between 0 and 150"
    )

    price: Decimal = Field(
        ...,
        gt=Decimal('0'),
        max_digits=10,
        decimal_places=2,
        description="Price with 2 decimal places"
    )

    quantity: StrictInt = Field(
        default=3,
        ge=3,
        multiple_of=3,
        description="Quantity must be positive integer"
    )

    # Collection constraints
    tags: List[str] = Field(
        default_factory=list,
        min_length=0,
        max_length=10,
        description="List of tags with max 10 items"
    )

    # Alias example
    user_id: int = Field(
        ...,
        alias="userId",
        gt=0,
        description="User ID with alias"
    )


class TestConstraintSchema:
    """Test cases for ConstraintTestSchema covering various constraint scenarios."""

    def test_valid_schema_creation(self):
        """Test creating schema with all valid values."""
        data = {
            "username": "test_user",
            "score": 85.5,
            "age": 25,
            "price": "99.99",
            "quantity": 3,
            "tags": ["python", "testing"],
            "userId": 123
        }

        schema = ConstraintTestSchema(**data)

        assert schema.username == "test_user"
        assert schema.score == 85.5
        assert schema.age == 25
        assert schema.price == Decimal('99.99')
        assert schema.quantity == 3
        assert schema.tags == ["python", "testing"]
        assert schema.user_id == 123

    def test_string_min_length_constraint(self):
        """Test string minimum length constraint."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="ab",  # Too short
                score=85.5,
                age=25,
                price="99.99",
                quantity=3,
                tags=["python", "testing"],
                userId=123
            )

        error = exc_info.value.errors()[0]
        assert error['type'] == 'string_too_short'
        assert error['loc'] == ('username',)

    def test_string_max_length_constraint(self):
        """Test string maximum length constraint."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="a" * 25,  # Too long
                score=85.5,
                age=25,
                price="99.99",
                quantity=3,
                tags=["python", "testing"],
                userId=123
            )

        error = exc_info.value.errors()[0]
        assert error['type'] == 'string_too_long'
        assert error['loc'] == ('username',)

    def test_string_pattern_constraint(self):
        """Test string pattern constraint."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="test-user!",  # Invalid characters
                score=85.5,
                age=25,
                price="99.99",
                quantity=3,
                tags=["python", "testing"],
                userId=123
            )

        error = exc_info.value.errors()[0]
        assert error['type'] == 'string_pattern_mismatch'
        assert error['loc'] == ('username',)

    def test_numeric_ge_constraint(self):
        """Test numeric greater than or equal constraint."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="testuser",
                score=-1,
                age=25,
                price="99.99",
                quantity=3,
                tags=["python", "testing"],
                userId=123
            )

        error = exc_info.value.errors()[0]
        assert error['type'] == 'greater_than_equal'
        assert error['loc'] == ('score',)

    def test_numeric_le_constraint(self):
        """Test numeric less than or equal constraint."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="testuser",
                score=101,
                age=25,
                price="99.99",
                quantity=3,
                tags=["python", "testing"],
                userId=123
            )

        error = exc_info.value.errors()[0]
        assert error['type'] == 'less_than_equal'
        assert error['loc'] == ('score',)

    def test_numeric_gt_constraint(self):
        """Test numeric greater than constraint."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="testuser",
                score=0.0,
                age=0,
                price="99.99",
                quantity=3,
                tags=["python", "testing"],
                userId=123
            )

        error = exc_info.value.errors()[0]
        assert error['type'] == 'greater_than'
        assert error['loc'] == ('age',)

    def test_numeric_lt_constraint(self):
        """Test numeric less than constraint."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="testuser",
                score=92,
                age=150,
                price="99.99",
                quantity=3,
                tags=["python", "testing"],
                userId=123
            )

        error = exc_info.value.errors()[0]
        assert error['type'] == 'less_than'
        assert error['loc'] == ('age',)

    def test_decimal_constraints(self):
        """Test decimal field constraints."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="testuser",
                score=85.5,
                age=25,
                price="0",
                quantity=3,
                tags=["python", "testing"],
                userId=123
            )

        error = exc_info.value.errors()[0]
        assert error['type'] == 'greater_than'
        assert error['loc'] == ('price',)

    def test_decimal_precision_constraint(self):
        """Test decimal precision constraint."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="testuser",
                score=85.5,
                age=25,
                price="99.999",  # Too many decimal places
                quantity=3,
                tags=["python", "testing"],
                userId=123
            )

        error = exc_info.value.errors()[0]
        assert error['type'] == 'decimal_max_places'
        assert error['loc'] == ('price',)

    def test_list_min_length_constraint(self):
        """Test list minimum length constraint."""
        # This should pass as min_length=0
        schema = ConstraintTestSchema(
            username="testuser",
            email="test@example.com",
            age=25,
            score=85.5,
            price="99.99",
            tags=[],  # Empty list is allowed
            categories={"tech"},
            userId=123
        )
        assert schema.tags == []

    def test_list_max_length_constraint(self):
        """Test list maximum length constraint."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="testuser",
                score=85.5,
                age=25,
                price="99.99",
                tags=["tag" + str(i) for i in range(15)],  # Too many tags
                quantity=3,
                userId=123
            )

        error = exc_info.value.errors()[0]
        assert error['type'] == 'too_long'
        assert error['loc'] == ('tags',)

    def test_field_alias_constraint(self):
        """Test field alias constraint."""
        # Should work with alias
        schema = ConstraintTestSchema(
            username="testuser",
            score=85.5,
            age=25,
            price="99.99",
            quantity=3,
            tags=["python", "testing"],
            userId=123  # Using alias
        )
        assert schema.user_id == 123

        # Should fail without alias
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="testuser",
                score=85.5,
                age=25,
                price="99.99",
                quantity=3,
                tags=["python", "testing"],
                user_id=123  # Using field name instead of alias
            )

        error = exc_info.value.errors()[0]
        assert error['type'] == 'missing'
        assert 'userId' in str(exc_info.value)

    def test_multiple_constraint_violations(self):
        """Test multiple constraint violations in single validation."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintTestSchema(
                username="ab",  # Too short
                age=-5,  # Below minimum
                score=150.0,  # Above maximum
                price="0",  # Not greater than 0
                userId=-1  # Not greater than 0
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 5  # Should have multiple errors

        error_types = [error['type'] for error in errors]
        assert 'string_too_short' in error_types
        assert 'greater_than' in error_types
        assert 'less_than_equal' in error_types
