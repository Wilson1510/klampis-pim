from sqlalchemy import String, event, Text, Integer, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import pytest
import uuid

from app.core.base import Base
from app.models import Products, Skus, SkuAttributeValue, PriceDetails
from app.core.listeners import _set_slug
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    assert_relationship,
    count_model_objects
)


@pytest.fixture
async def setup_skus(sku_factory, product_factory):
    """Fixture to create skus for the test suite"""
    test_product = await product_factory()
    test_sku1 = await sku_factory(
        name="Test Sku 1",
        description="Test Sku 1 description",
        product=test_product
    )
    test_sku2 = await sku_factory(
        name="Test Sku 2",
        description="Test Sku 2 description",
        product=test_product
    )
    return test_product, test_sku1, test_sku2


class TestSku:
    """Test suite for Sku model and relationships"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_skus):
        """Setup method for the test suite"""
        self.test_product, self.test_sku1, self.test_sku2 = setup_skus

    def test_inheritance_from_base_model(self):
        """Test that Sku model inherits from Base model"""
        assert issubclass(Skus, Base)

    def test_fields_with_validation(self):
        """Test that Sku model has fields with validation"""
        assert hasattr(Skus, 'validate_sku_number')
        assert not hasattr(Skus, 'validate_name')
        assert len(Skus.__mapper__.validators) == 1

    def test_has_listeners(self):
        """Test that the model has the expected listeners"""
        assert event.contains(Skus.name, 'set', _set_slug)
        assert not event.contains(Skus, 'set', _set_slug)

    def test_name_field_properties(self):
        """Test the properties of the name field"""
        name_column = Skus.__table__.columns.get('name')
        assert name_column is not None
        assert isinstance(name_column.type, String)
        assert name_column.type.length == 100
        assert name_column.nullable is False
        assert name_column.unique is None
        assert name_column.index is True
        assert name_column.default is None

    def test_slug_field_properties(self):
        """Test the properties of the slug field"""
        slug_column = Skus.__table__.columns.get('slug')
        assert slug_column is not None
        assert isinstance(slug_column.type, String)
        assert slug_column.type.length == 100
        assert slug_column.nullable is False
        assert slug_column.unique is True
        assert slug_column.index is True
        assert slug_column.default is None

    def test_description_field_properties(self):
        """Test the properties of the description field"""
        description_column = Skus.__table__.columns.get('description')
        assert description_column is not None
        assert isinstance(description_column.type, Text)
        assert description_column.nullable is True
        assert description_column.unique is None
        assert description_column.index is None
        assert description_column.default is None

    def test_sku_number_field_properties(self):
        """Test the properties of the sku_number field"""
        sku_number_column = Skus.__table__.columns.get('sku_number')
        assert sku_number_column is not None
        assert isinstance(sku_number_column.type, String)
        assert sku_number_column.type.length == 10
        assert sku_number_column.nullable is False
        assert sku_number_column.unique is True
        assert sku_number_column.index is True
        assert sku_number_column.default.is_callable is True

    def test_product_id_field_properties(self):
        """Test the properties of the product_id field"""
        product_id_column = Skus.__table__.columns.get('product_id')
        assert product_id_column is not None
        assert isinstance(product_id_column.type, Integer)
        assert product_id_column.nullable is False
        foreign_key = list(product_id_column.foreign_keys)[0]
        assert str(foreign_key.target_fullname) == "products.id"
        assert product_id_column.unique is None
        assert product_id_column.index is True
        assert product_id_column.default is None

    def test_relationships_with_other_models(self):
        """Test the relationships with other models"""
        assert_relationship(Skus, "product", "skus")

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_sku1)
        assert str_repr == "Skus(Test Sku 1)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        assert self.test_sku1.id == 1
        assert self.test_sku1.name == "Test Sku 1"
        assert self.test_sku1.slug == "test-sku-1"
        assert self.test_sku1.description == "Test Sku 1 description"
        assert self.test_sku1.sku_number is not None
        assert len(self.test_sku1.sku_number) == 10
        assert self.test_sku1.product_id == self.test_product.id
        assert self.test_sku1.product == self.test_product

        assert self.test_sku2.id == 2
        assert self.test_sku2.name == "Test Sku 2"
        assert self.test_sku2.slug == "test-sku-2"
        assert self.test_sku2.description == "Test Sku 2 description"
        assert self.test_sku2.sku_number is not None
        assert len(self.test_sku2.sku_number) == 10
        assert self.test_sku2.product_id == self.test_product.id
        assert self.test_sku2.product == self.test_product

        # sku_number should be unique
        assert self.test_sku1.sku_number != self.test_sku2.sku_number

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = Skus(
            name="test sku 3",
            description="test sku 3 description",
            product_id=self.test_product.id
        )
        await save_object(db_session, item)

        assert item.id == 3
        assert item.name == "test sku 3"
        assert item.slug == "test-sku-3"
        assert item.description == "test sku 3 description"
        assert item.sku_number is not None
        assert item.product_id == self.test_product.id
        assert await count_model_objects(db_session, Skus) == 3

        item_with_slug_and_sku = Skus(
            name="test sku 4",
            slug="slug-sku-4",
            sku_number="BE1258DFEE",
            description="test sku 4 description",
            product_id=self.test_product.id
        )
        await save_object(db_session, item_with_slug_and_sku)
        assert item_with_slug_and_sku.id == 4
        assert item_with_slug_and_sku.name == "test sku 4"
        # slug should be set to the slugified name, not the one provided
        assert item_with_slug_and_sku.slug == "test-sku-4"
        # sku_number should be set to the one provided
        assert item_with_slug_and_sku.sku_number == "BE1258DFEE"
        assert item_with_slug_and_sku.description == "test sku 4 description"
        assert item_with_slug_and_sku.product_id == self.test_product.id
        assert await count_model_objects(db_session, Skus) == 4

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(db_session, Skus, self.test_sku1.id)
        assert item.id == 1
        assert item.name == "Test Sku 1"
        assert item.slug == "test-sku-1"
        assert item.description == "Test Sku 1 description"
        assert item.product_id == self.test_product.id

        item = await get_object_by_id(db_session, Skus, self.test_sku2.id)
        assert item.id == 2
        assert item.name == "Test Sku 2"
        assert item.slug == "test-sku-2"
        assert item.description == "Test Sku 2 description"
        assert item.product_id == self.test_product.id

        items = await get_all_objects(db_session, Skus)
        assert len(items) == 2

        assert items[0].id == 1
        assert items[0].name == "Test Sku 1"
        assert items[0].slug == "test-sku-1"
        assert items[0].description == "Test Sku 1 description"
        assert items[0].product_id == self.test_product.id

        assert items[1].id == 2
        assert items[1].name == "Test Sku 2"
        assert items[1].slug == "test-sku-2"
        assert items[1].description == "Test Sku 2 description"
        assert items[1].product_id == self.test_product.id

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(db_session, Skus, self.test_sku1.id)
        original_sku_number = item.sku_number

        item.name = "updated test sku 1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test sku 1"
        assert item.slug == "updated-test-sku-1"
        assert item.sku_number == original_sku_number  # should not change on update
        assert item.description == "Test Sku 1 description"
        assert item.product_id == self.test_product.id
        assert await count_model_objects(db_session, Skus) == 2

        item.slug = "updated-slug-sku-1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test sku 1"
        # slug should keep the same as it's generated from name
        assert item.slug == "updated-test-sku-1"
        assert await count_model_objects(db_session, Skus) == 2

        item.sku_number = uuid.uuid4().hex[:10].upper()
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test sku 1"
        assert item.sku_number is not None
        assert len(item.sku_number) == 10
        assert item.sku_number != original_sku_number

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_sku2)

        item = await get_object_by_id(db_session, Skus, self.test_sku2.id)
        assert item is None
        assert await count_model_objects(db_session, Skus) == 1


class TestSkuValidationDatabase:
    """Test suite for Sku model validation database"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_skus):
        """Setup method for the test suite"""
        self.test_product, self.test_sku1, self.test_sku2 = setup_skus

    @pytest.mark.asyncio
    async def test_valid_sku_number_database_constraint(self, db_session: AsyncSession):
        """Test valid sku_number passes database constraint"""
        valid_sku_numbers = [
            "ABCDEF1234",
            "1234567890",
            "FFFFFFFFFF"
        ]
        for i, sku_num in enumerate(valid_sku_numbers):
            sql = text("""
                INSERT INTO skus (
                    name,
                    slug,
                    product_id,
                    sku_number,
                    is_active,
                    sequence,
                    created_by,
                    updated_by
                )
                VALUES (
                    :name,
                    :slug,
                    :product_id,
                    :sku_number,
                    :is_active,
                    :sequence,
                    :created_by,
                    :updated_by
                )
            """)
            await db_session.execute(sql, {
                'name': f"Valid SKU Number {i}",
                'slug': f"valid-sku-number-{i}",
                'product_id': self.test_product.id,
                'sku_number': sku_num,
                'is_active': True,
                'sequence': 1,
                'created_by': 1,
                'updated_by': 1
            })
            await db_session.commit()

            stmt = select(Skus).where(Skus.sku_number == sku_num)
            result = await db_session.execute(stmt)
            sku = result.scalar_one_or_none()
            assert sku.sku_number == sku_num

    @pytest.mark.asyncio
    async def test_invalid_sku_number_database_constraint(
        self, db_session: AsyncSession
    ):
        """Test invalid sku_number fails database constraint"""
        invalid_sku_numbers = [
            "AAABB1",
            "ABCDEFG123",
            "  ABCDE-14",
            "def123Gbc4",
            "AAABBBCCD ",
            "BBBCCCdDDE"
        ]
        product_id = self.test_product.id
        for invalid_sku_number in invalid_sku_numbers:
            sql = text("""
                INSERT INTO skus (
                    name,
                    slug,
                    product_id,
                    sku_number,
                    is_active,
                    sequence,
                    created_by,
                    updated_by
                )
                VALUES (
                    :name,
                    :slug,
                    :product_id,
                    :sku_number,
                    :is_active,
                    :sequence,
                    :created_by,
                    :updated_by
                )
            """)
            with pytest.raises(
                IntegrityError,
                match="check_skus_sku_number_format"
            ):
                await db_session.execute(sql, {
                    'name': "Invalid Length SKU",
                    'slug': "invalid-length-sku",
                    'product_id': product_id,
                    'sku_number': invalid_sku_number,
                    'is_active': True,
                    'sequence': 1,
                    'created_by': 1,
                    'updated_by': 1
                })
            await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_sku_number_invalid_database_constraint(
        self, db_session: AsyncSession
    ):
        """Test updating sku_number with invalid value fails database constraint"""
        # Create valid sku first
        sku = Skus(
            name="Valid SKU",
            product_id=self.test_product.id,
            sku_number="ABCDEF1234"
        )
        await save_object(db_session, sku)

        sku_id = sku.id

        invalid_sku_numbers = [
            "AAABB1",
            "ABCDEFG123",
            "  ABCDE-14",
            "def123Gbc4",
            "AAABBBCCD ",
            "BBBCCCdDDE"
        ]

        # Try to update with invalid file name using raw SQL to bypass
        # application validation
        for invalid_sku_number in invalid_sku_numbers:
            sql = text("""
                UPDATE skus
                SET sku_number = :new_sku_number
                WHERE id = :sku_id
            """)

            with pytest.raises(
                IntegrityError, match="check_skus_sku_number_format"
            ):
                await db_session.execute(sql, {
                    'new_sku_number': invalid_sku_number,
                    'sku_id': sku_id
                })
            await db_session.rollback()


class TestSkuValidationApplication:
    """Test suite for Sku model validation"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_skus):
        """Setup method for the test suite"""
        self.test_product, self.test_sku1, self.test_sku2 = setup_skus

    def test_valid_sku_number_validation(self):
        """Test valid sku_number validation"""
        valid_sku_numbers = [
            ("ABCDEF1234", "ABCDEF1234"),
            (" 1234567890", "1234567890"),
            ("a1b2C3d4E5 ", "A1B2C3D4E5"),
            ("FFFFFFFFFF", "FFFFFFFFFF"),
            ("  ABCfdF1234  ", "ABCFDF1234")
        ]
        for i, (sku_num, expected_sku_num) in enumerate(valid_sku_numbers):
            sku = Skus(
                name=f"Valid SKU {i}",
                product_id=self.test_product.id,
                sku_number=sku_num
            )
            assert sku.sku_number == expected_sku_num

    def test_invalid_sku_number_validation(self):
        """Test invalid sku_number validation"""
        product_id = self.test_product.id
        # Test for length
        invalid_length_skus = ["12345", "12345678901", "  ABCfdF12345  "]
        for sku_num in invalid_length_skus:
            with pytest.raises(
                ValueError,
                match="SKU number must be exactly 10 characters long."
            ):
                Skus(
                    name="Invalid Length SKU",
                    product_id=product_id,
                    sku_number=sku_num
                )

        # Test for invalid characters
        invalid_char_skus = ["GHIJKLM123", "ABC-123-DE", "  ABCDE-1234"]
        for sku_num in invalid_char_skus:
            with pytest.raises(
                ValueError,
                match="SKU number must only contain 0-9 or A-F characters."
            ):
                Skus(
                    name="Invalid Char SKU",
                    product_id=product_id,
                    sku_number=sku_num
                )

    def test_update_to_invalid_sku_number(self):
        """Test updating to an invalid sku_number"""
        sku = Skus(
            name="Invalid SKU Number",
            product_id=self.test_product.id,
            sku_number="ABCDEF1234"
        )
        invalid_length_skus = ["12345", "12345678901", "  ABCfdF12345  "]
        for sku_num in invalid_length_skus:
            with pytest.raises(
                ValueError,
                match="SKU number must be exactly 10 characters long."
            ):
                sku.sku_number = sku_num

        invalid_char_skus = ["GHIJKLM123", "ABC-123-DE", " ABCDE-1234"]
        for sku_num in invalid_char_skus:
            with pytest.raises(
                ValueError,
                match="SKU number must only contain 0-9 or A-F characters."
            ):
                sku.sku_number = sku_num


class TestSkuProductRelationship:
    """Test suite for Sku model relationships with Product model"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_skus):
        """Setup method for the test suite"""
        self.test_product, self.test_sku1, self.test_sku2 = setup_skus

    @pytest.mark.asyncio
    async def test_sku_with_product_relationship(self, db_session: AsyncSession):
        """Test sku with product relationship properly loads"""
        retrieved_sku = await get_object_by_id(
            db_session,
            Skus,
            self.test_sku1.id
        )

        assert retrieved_sku.product_id == self.test_product.id
        assert retrieved_sku.product == self.test_product
        assert retrieved_sku.product.name == "Test Product"

    @pytest.mark.asyncio
    async def test_sku_without_product_relationship(self, db_session: AsyncSession):
        """Test sku without product relationship"""
        item = Skus(
            name="test sku without product",
            description="test description"
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_sku_to_different_product(
        self, db_session: AsyncSession, product_factory
    ):
        """Test updating a sku to use a different product"""
        # Create another product
        another_product = await product_factory(
            name="Another Test Product",
            description="Another test product description"
        )

        # Create sku with first product
        sku = Skus(
            name="test sku change product",
            description="test description",
            product_id=self.test_product.id
        )
        await save_object(db_session, sku)

        # Verify initially has first product
        assert sku.product_id == self.test_product.id
        assert sku.product == self.test_product
        assert sku.product.name == "Test Product"

        # Update to use different product
        sku.product_id = another_product.id
        await save_object(db_session, sku)

        # Verify product relationship is now the other one
        assert sku.product_id == another_product.id
        assert sku.product == another_product
        assert sku.product.name == "Another Test Product"

    @pytest.mark.asyncio
    async def test_create_sku_with_invalid_product_id(self, db_session: AsyncSession):
        """Test creating sku with non-existent product_id raises error"""
        sku = Skus(
            name="test invalid product",
            description="test description",
            product_id=999  # Non-existent ID
        )

        with pytest.raises(IntegrityError):
            await save_object(db_session, sku)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_sku_with_invalid_product_id(self, db_session: AsyncSession):
        """Test updating sku with non-existent product_id raises error"""
        sku = Skus(
            name="test invalid product update",
            description="test description",
            product_id=self.test_product.id
        )
        await save_object(db_session, sku)

        # Update with invalid product_id
        sku.product_id = 999  # Non-existent ID

        with pytest.raises(IntegrityError):
            await save_object(db_session, sku)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_setting_product_id_to_null_fails(self, db_session: AsyncSession):
        """Test that setting a SKU's product_id to None fails"""
        # Create a valid sku
        sku = Skus(
            name="SKU for null test",
            product_id=self.test_product.id
        )
        await save_object(db_session, sku)

        # Try to set product_id to None
        sku.product_id = None
        with pytest.raises(IntegrityError):
            await save_object(db_session, sku)

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_sku_with_product_relationship(self, db_session: AsyncSession):
        """Test deleting a sku that has product relationship"""
        # Create sku with product
        sku = Skus(
            name="test delete with product",
            description="test description",
            product_id=self.test_product.id
        )
        await save_object(db_session, sku)

        product = await get_object_by_id(
            db_session,
            Products,
            self.test_product.id
        )

        await db_session.refresh(product, ['skus'])

        assert product.skus == [self.test_sku1, self.test_sku2, sku]

        # Delete the sku
        await delete_object(db_session, sku)

        # Verify sku is deleted
        deleted_sku = await get_object_by_id(
            db_session, Skus, sku.id
        )
        assert deleted_sku is None

        # Verify product still exists (should not be affected)
        await db_session.refresh(product, ['skus'])
        assert product is not None
        assert product.name == "Test Product"
        assert product.skus == [self.test_sku1, self.test_sku2]


class TestSkuSkuAttributeValueRelationship:
    """Test suite for Sku model relationships with SkuAttributeValue model"""

    @pytest.fixture(autouse=True)
    async def setup_objects(self, setup_skus, attribute_factory):
        """Setup method for the test suite"""
        self.test_product, self.test_sku1, self.test_sku2 = setup_skus
        self.test_attribute1 = await attribute_factory(name="Test Attribute 1")
        self.test_attribute2 = await attribute_factory(name="Test Attribute 2")

    @pytest.mark.asyncio
    async def test_create_sku_with_sku_attribute_values(self, db_session: AsyncSession):
        """Test creating sku with sku attribute values"""
        sku = Skus(
            name="Test Sku with Sku Attribute Values",
            product_id=self.test_product.id,
            sku_attribute_values=[
                SkuAttributeValue(
                    attribute_id=self.test_attribute1.id,
                    value="Test Sku Attribute Value 1"
                ),
                SkuAttributeValue(
                    attribute_id=self.test_attribute2.id,
                    value="Test Sku Attribute Value 2"
                )
            ]
        )
        await save_object(db_session, sku)

        retrieved_sku = await get_object_by_id(
            db_session,
            Skus,
            sku.id
        )
        await db_session.refresh(retrieved_sku, ['sku_attribute_values'])

        assert retrieved_sku.id == 3
        assert retrieved_sku.name == "Test Sku with Sku Attribute Values"
        assert len(retrieved_sku.sku_attribute_values) == 2
        assert retrieved_sku.sku_attribute_values[0].value == (
            "Test Sku Attribute Value 1"
        )
        assert retrieved_sku.sku_attribute_values[1].value == (
            "Test Sku Attribute Value 2"
        )

    @pytest.mark.asyncio
    async def test_add_multiple_sku_attribute_values_to_sku(
        self, db_session: AsyncSession
    ):
        """Test adding multiple sku attribute values to sku"""
        sku_id = self.test_sku1.id
        attribute_id = self.test_attribute1.id
        for i in range(5):
            sku_attribute_value = SkuAttributeValue(
                value=f"Test Sku Attribute Value {i}",
                sku_id=sku_id,
                attribute_id=attribute_id
            )

            if i >= 1:
                # should fail because sku_id and attribute_id are no longer unique
                with pytest.raises(IntegrityError):
                    await save_object(db_session, sku_attribute_value)
                await db_session.rollback()
            else:
                await save_object(db_session, sku_attribute_value)

    @pytest.mark.asyncio
    async def test_update_skus_sku_attribute_values(self, db_session: AsyncSession):
        """Test updating sku sku attribute values"""
        sku = await get_object_by_id(
            db_session,
            Skus,
            self.test_sku1.id
        )
        await db_session.refresh(sku, ['sku_attribute_values'])
        assert len(sku.sku_attribute_values) == 0

        sku.sku_attribute_values = [
            SkuAttributeValue(
                value="Test Sku Attribute Value 1",
                attribute_id=self.test_attribute1.id
            ),
            SkuAttributeValue(
                value="Test Sku Attribute Value 2",
                attribute_id=self.test_attribute2.id
            )
        ]
        await save_object(db_session, sku)
        await db_session.refresh(sku, ['sku_attribute_values'])
        assert len(sku.sku_attribute_values) == 2
        assert sku.sku_attribute_values[0].value == "Test Sku Attribute Value 1"
        assert sku.sku_attribute_values[1].value == "Test Sku Attribute Value 2"

        sku.sku_attribute_values = [
            SkuAttributeValue(
                value="Test Sku Attribute Value 3",
                attribute_id=self.test_attribute1.id
            )
        ]
        with pytest.raises(IntegrityError):
            # should fail because Test Sku Attribute Value 1 and Test Sku Attribute
            # Value 2 no longer have sku_id
            await save_object(db_session, sku)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_sku_deletion_with_sku_attribute_values(
        self, db_session: AsyncSession
    ):
        """Test deleting a sku that has sku attribute values"""
        sku_attribute_value = SkuAttributeValue(
            value="Test Sku Attribute Value 1",
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute1.id
        )
        await save_object(db_session, sku_attribute_value)
        await db_session.refresh(sku_attribute_value, ['sku'])
        assert sku_attribute_value.sku_id == self.test_sku1.id

        # should fail because sku_attribute_value will lose its sku_id
        with pytest.raises(IntegrityError):
            await delete_object(db_session, self.test_sku1)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_orphaned_sku_attribute_value_cleanup(self, db_session: AsyncSession):
        """Test orphaned sku attribute value cleanup"""
        temp_sku = Skus(
            name="Temporary Sku for Sku Attribute Value Cleanup",
            product_id=self.test_product.id
        )
        await save_object(db_session, temp_sku)

        temp_sku_attribute_value = SkuAttributeValue(
            value="Temporary Sku Attribute Value",
            sku_id=temp_sku.id,
            attribute_id=self.test_attribute1.id
        )
        await save_object(db_session, temp_sku_attribute_value)

        # Try to delete the sku (should fail because of foreign key)
        with pytest.raises(IntegrityError):
            await delete_object(db_session, temp_sku)
        await db_session.rollback()

        # To properly delete, first remove the sku attribute value
        await delete_object(db_session, temp_sku_attribute_value)
        await delete_object(db_session, temp_sku)

        # Verify both are deleted
        deleted_sku = await get_object_by_id(
            db_session,
            Skus,
            temp_sku.id
        )
        deleted_sku_attribute_value = await get_object_by_id(
            db_session,
            SkuAttributeValue,
            temp_sku_attribute_value.id
        )
        assert deleted_sku is None
        assert deleted_sku_attribute_value is None

    @pytest.mark.asyncio
    async def test_query_sku_by_sku_attribute_value(self, db_session: AsyncSession):
        """Test querying sku by sku attribute value"""
        sku_attribute_value1 = SkuAttributeValue(
            value="Test Sku Attribute Value 1",
            sku_id=self.test_sku1.id,
            attribute_id=self.test_attribute1.id
        )
        await save_object(db_session, sku_attribute_value1)

        sku_attribute_value2 = SkuAttributeValue(
            value="Test Sku Attribute Value 2",
            sku_id=self.test_sku2.id,
            attribute_id=self.test_attribute1.id
        )
        await save_object(db_session, sku_attribute_value2)

        stmt = select(Skus).join(Skus.sku_attribute_values).where(
            SkuAttributeValue.value == "Test Sku Attribute Value 1"
        )
        result = await db_session.execute(stmt)
        skus = result.scalars().all()
        assert len(skus) == 1
        assert self.test_sku1 in skus


class TestSkuPriceDetailRelationship:
    """Test suite for Sku model relationships with PriceDetail model"""

    @pytest.fixture(autouse=True)
    async def setup_objects(self, setup_skus, pricelist_factory):
        """Setup method for the test suite"""
        self.test_product, self.test_sku1, self.test_sku2 = setup_skus
        self.test_pricelist = await pricelist_factory()

    @pytest.mark.asyncio
    async def test_create_sku_with_price_details(self, db_session: AsyncSession):
        """Test creating sku with price details"""
        sku = Skus(
            name="Test Sku with Price Details",
            product_id=self.test_product.id,
            price_details=[
                PriceDetails(
                    price=100.00,
                    minimum_quantity=1,
                    pricelist_id=self.test_pricelist.id
                ),
                PriceDetails(
                    price=200.00,
                    minimum_quantity=2,
                    pricelist_id=self.test_pricelist.id
                )
            ]
        )
        await save_object(db_session, sku)

        retrieved_sku = await get_object_by_id(
            db_session,
            Skus,
            sku.id
        )
        await db_session.refresh(retrieved_sku, ['price_details'])

        assert retrieved_sku.id == 3
        assert retrieved_sku.name == "Test Sku with Price Details"
        assert len(retrieved_sku.price_details) == 2
        assert retrieved_sku.price_details[0].price == 100.00
        assert retrieved_sku.price_details[0].minimum_quantity == 1
        assert retrieved_sku.price_details[0].pricelist_id == self.test_pricelist.id
        assert retrieved_sku.price_details[1].price == 200.00
        assert retrieved_sku.price_details[1].minimum_quantity == 2
        assert retrieved_sku.price_details[1].pricelist_id == self.test_pricelist.id

    @pytest.mark.asyncio
    async def test_add_multiple_price_details_to_sku(self, db_session: AsyncSession):
        """Test adding multiple price details to sku"""
        for i in range(5):
            price_detail = PriceDetails(
                price=100.00 * (i + 1),
                minimum_quantity=i + 1,
                pricelist_id=self.test_pricelist.id,
                sku_id=self.test_sku1.id
            )
            await save_object(db_session, price_detail)

        retrieved_sku = await get_object_by_id(
            db_session,
            Skus,
            self.test_sku1.id
        )
        await db_session.refresh(retrieved_sku, ['price_details'])
        assert len(retrieved_sku.price_details) == 5
        for i in range(5):
            assert retrieved_sku.price_details[i].id == i + 1
            assert retrieved_sku.price_details[i].price == 100.00 * (i + 1)
            assert retrieved_sku.price_details[i].minimum_quantity == i + 1
            assert retrieved_sku.price_details[i].pricelist_id == self.test_pricelist.id

    @pytest.mark.asyncio
    async def test_update_skus_price_details(self, db_session: AsyncSession):
        """Test updating sku price details"""
        sku = await get_object_by_id(
            db_session,
            Skus,
            self.test_sku1.id
        )
        await db_session.refresh(sku, ['price_details'])
        assert len(sku.price_details) == 0

        sku.price_details = [
            PriceDetails(
                price=100.00,
                minimum_quantity=1,
                pricelist_id=self.test_pricelist.id
            ),
            PriceDetails(
                price=200.00,
                minimum_quantity=2,
                pricelist_id=self.test_pricelist.id
            )
        ]
        await save_object(db_session, sku)
        await db_session.refresh(sku, ['price_details'])
        assert len(sku.price_details) == 2
        assert sku.price_details[0].price == 100.00
        assert sku.price_details[1].price == 200.00

        sku.price_details = [
            PriceDetails(
                price=300.00,
                minimum_quantity=3,
                pricelist_id=self.test_pricelist.id
            ),
            PriceDetails(
                price=400.00,
                minimum_quantity=4,
                pricelist_id=self.test_pricelist.id
            ),
            PriceDetails(
                price=500.00,
                minimum_quantity=5,
                pricelist_id=self.test_pricelist.id
            )
        ]

        # should fail because price_details[0] and price_details[1] will lose their
        # sku_id
        with pytest.raises(IntegrityError):
            await save_object(db_session, sku)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_sku_deletion_with_price_details(self, db_session: AsyncSession):
        """Test deleting a sku that has price details"""
        price_detail = PriceDetails(
            price=100.00,
            minimum_quantity=1,
            pricelist_id=self.test_pricelist.id,
            sku_id=self.test_sku1.id
        )
        await save_object(db_session, price_detail)

        # should fail because price_detail will lose its sku_id
        with pytest.raises(IntegrityError):
            await delete_object(db_session, self.test_sku1)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_orphaned_price_detail_cleanup(self, db_session: AsyncSession):
        """Test orphaned price detail cleanup"""
        temp_sku = Skus(
            name="Temporary Sku for Price Detail Cleanup",
            product_id=self.test_product.id
        )
        await save_object(db_session, temp_sku)

        temp_price_detail = PriceDetails(
            price=100.00,
            minimum_quantity=1,
            pricelist_id=self.test_pricelist.id,
            sku_id=temp_sku.id
        )
        await save_object(db_session, temp_price_detail)

        # Try to delete the sku (should fail because of foreign key)
        with pytest.raises(IntegrityError):
            await delete_object(db_session, temp_sku)
        await db_session.rollback()

        # To properly delete, first remove the price detail
        await delete_object(db_session, temp_price_detail)
        await delete_object(db_session, temp_sku)

        # Verify both are deleted
        deleted_sku = await get_object_by_id(
            db_session,
            Skus,
            temp_sku.id
        )
        deleted_price_detail = await get_object_by_id(
            db_session,
            PriceDetails,
            temp_price_detail.id
        )
        assert deleted_sku is None
        assert deleted_price_detail is None

    @pytest.mark.asyncio
    async def test_query_sku_by_price_detail(self, db_session: AsyncSession):
        """Test querying sku by price detail"""
        price_detail = PriceDetails(
            price=100.00,
            minimum_quantity=1,
            pricelist_id=self.test_pricelist.id,
            sku_id=self.test_sku1.id
        )
        await save_object(db_session, price_detail)

        price_detail2 = PriceDetails(
            price=200.00,
            minimum_quantity=2,
            pricelist_id=self.test_pricelist.id,
            sku_id=self.test_sku2.id
        )
        await save_object(db_session, price_detail2)

        stmt = select(Skus).join(Skus.price_details).where(
            PriceDetails.price == 100.00
        )
        result = await db_session.execute(stmt)
        sku = result.scalar_one_or_none()
        assert sku.id == self.test_sku1.id
        assert sku.name == "Test Sku 1"
        assert sku.slug == "test-sku-1"
