from sqlalchemy import Integer, UniqueConstraint, Numeric
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import pytest

from app.core.base import Base
from app.models import Pricelists, Skus, PriceDetails
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    assert_relationship,
    count_model_objects
)


@pytest.fixture
async def setup_price_details(sku_factory, pricelist_factory, price_detail_factory):
    """Fixture to create price details for the test suite"""
    test_sku = await sku_factory()
    test_pricelist = await pricelist_factory()
    test_price_detail1 = await price_detail_factory(
        price=100.00,
        minimum_quantity=1,
        sku=test_sku,
        pricelist=test_pricelist
    )
    test_price_detail2 = await price_detail_factory(
        price=200.00,
        minimum_quantity=2,
        sku=test_sku,
        pricelist=test_pricelist
    )
    return test_sku, test_pricelist, test_price_detail1, test_price_detail2


class TestPriceDetail:
    """Test suite for PriceDetail model and relationships"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_price_details):
        """Setup method for the test suite"""
        self.test_sku, self.test_pricelist, self.test_price_detail1, \
            self.test_price_detail2 = setup_price_details

    def test_inheritance_from_base_model(self):
        """Test that PriceDetail model inherits from Base model"""
        assert issubclass(PriceDetails, Base)

    def test_fields_with_validation(self):
        """Test that PriceDetail model has fields with validation"""
        assert not hasattr(PriceDetails, 'validate_price')
        assert len(PriceDetails.__mapper__.validators) == 0

    def test_table_args(self):
        """Test that PriceDetail model has the expected table args"""
        table_args = PriceDetails.__table_args__

        # Check that we have exactly 1 constraint
        assert len(table_args) == 1

        # Check that the constraint is a UniqueConstraint
        assert isinstance(table_args[0], UniqueConstraint)

        assert table_args[0].name == 'uq_price_detail'
        assert set(table_args[0].columns.keys()) == {
            'minimum_quantity',
            'sku_id',
            'pricelist_id'
        }

        assert not hasattr(table_args[0], 'sqltext')

    def test_price_field_properties(self):
        """Test that PriceDetail model has the expected price field properties"""
        price_column = PriceDetails.__table__.columns['price']
        assert price_column is not None
        assert isinstance(price_column.type, Numeric)
        assert price_column.type.precision == 15
        assert price_column.type.scale == 2
        assert price_column.nullable is False
        assert price_column.unique is None
        assert price_column.index is True
        assert price_column.default is None

    def test_minimum_quantity_field_properties(self):
        """
        Test that PriceDetail model has the expected minimum_quantity field properties
        """
        minimum_quantity_column = PriceDetails.__table__.columns['minimum_quantity']
        assert minimum_quantity_column is not None
        assert isinstance(minimum_quantity_column.type, Integer)
        assert minimum_quantity_column.nullable is False
        assert minimum_quantity_column.unique is None
        assert minimum_quantity_column.index is True
        assert minimum_quantity_column.default.arg == 1

    def test_sku_id_field_properties(self):
        """Test that PriceDetail model has the expected sku_id field properties"""
        sku_id_column = PriceDetails.__table__.columns['sku_id']
        assert sku_id_column is not None
        assert isinstance(sku_id_column.type, Integer)
        assert sku_id_column.nullable is False
        foreign_key = list(sku_id_column.foreign_keys)[0]
        assert str(foreign_key.target_fullname) == "skus.id"
        assert sku_id_column.unique is None
        assert sku_id_column.index is True
        assert sku_id_column.default is None

    def test_pricelist_id_field_properties(self):
        """Test that PriceDetail model has the expected pricelist_id field properties"""
        pricelist_id_column = PriceDetails.__table__.columns['pricelist_id']
        assert pricelist_id_column is not None
        assert isinstance(pricelist_id_column.type, Integer)
        assert pricelist_id_column.nullable is False
        foreign_key = list(pricelist_id_column.foreign_keys)[0]
        assert str(foreign_key.target_fullname) == "pricelists.id"
        assert pricelist_id_column.unique is None
        assert pricelist_id_column.index is True
        assert pricelist_id_column.default is None

    def test_relationships_with_other_models(self):
        """Test the relationships with other models"""
        assert_relationship(PriceDetails, "sku", "price_details")
        assert_relationship(PriceDetails, "pricelist", "price_details")

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_price_detail1)
        expected = ("PriceDetails(100.00, 1)")
        assert str_repr == expected

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        assert self.test_price_detail1.id == 1
        assert self.test_price_detail1.price == 100.00
        assert self.test_price_detail1.minimum_quantity == 1
        assert self.test_price_detail1.sku_id == self.test_sku.id
        assert self.test_price_detail1.pricelist_id == self.test_pricelist.id

        assert self.test_price_detail2.id == 2
        assert self.test_price_detail2.price == 200.00
        assert self.test_price_detail2.minimum_quantity == 2
        assert self.test_price_detail2.sku_id == self.test_sku.id
        assert self.test_price_detail2.pricelist_id == self.test_pricelist.id

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        await save_object(db_session, item)

        assert item.id == 3
        assert item.price == 300.00
        assert item.minimum_quantity == 3
        assert item.sku_id == self.test_sku.id
        assert item.pricelist_id == self.test_pricelist.id
        assert await count_model_objects(db_session, PriceDetails) == 3

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(
            db_session,
            PriceDetails,
            self.test_price_detail1.id
        )
        assert item.id == 1
        assert item.price == 100.00
        assert item.minimum_quantity == 1
        assert item.sku_id == self.test_sku.id
        assert item.pricelist_id == self.test_pricelist.id

        item = await get_object_by_id(
            db_session,
            PriceDetails,
            self.test_price_detail2.id
        )
        assert item.id == 2
        assert item.price == 200.00
        assert item.minimum_quantity == 2
        assert item.sku_id == self.test_sku.id
        assert item.pricelist_id == self.test_pricelist.id

        items = await get_all_objects(db_session, PriceDetails)
        assert len(items) == 2

        assert items[0].id == 1
        assert items[0].price == 100.00
        assert items[0].minimum_quantity == 1
        assert items[0].sku_id == self.test_sku.id
        assert items[0].pricelist_id == self.test_pricelist.id

        assert items[1].id == 2
        assert items[1].price == 200.00
        assert items[1].minimum_quantity == 2
        assert items[1].sku_id == self.test_sku.id
        assert items[1].pricelist_id == self.test_pricelist.id

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(
            db_session,
            PriceDetails,
            self.test_price_detail1.id
        )
        item.price = 150.00
        item.minimum_quantity = 3
        await save_object(db_session, item)

        assert item.id == 1
        assert item.price == 150.00
        assert item.minimum_quantity == 3
        assert item.sku_id == self.test_sku.id
        assert item.pricelist_id == self.test_pricelist.id
        assert await count_model_objects(db_session, PriceDetails) == 2

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_price_detail1)

        item = await get_object_by_id(
            db_session,
            PriceDetails,
            self.test_price_detail1.id
        )
        assert item is None
        assert await count_model_objects(db_session, PriceDetails) == 1


class TestPriceDetailValidationDatabase:
    """Test suite for PriceDetail model constraints"""

    @pytest.fixture(autouse=True)
    async def setup_objects(self, setup_price_details, pricelist_factory, sku_factory):
        """Setup method for the test suite"""
        self.test_sku, self.test_pricelist, self.test_price_detail1, \
            self.test_price_detail2 = setup_price_details
        self.another_pricelist = await pricelist_factory(name="Another Pricelist")
        self.another_sku = await sku_factory(name="Another SKU")

    @pytest.mark.asyncio
    async def test_create_item_same_all_fields(
        self, db_session: AsyncSession
    ):
        """
        Test the create operation with same all fields fail.
        """
        duplicate_price_detail = PriceDetails(
            price=100.00,
            minimum_quantity=1,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )

        with pytest.raises(IntegrityError):
            await save_object(db_session, duplicate_price_detail)

        await db_session.rollback()

        assert await count_model_objects(db_session, PriceDetails) == 2

    @pytest.mark.asyncio
    async def test_update_item_same_all_fields(
        self, db_session: AsyncSession
    ):
        """
        Test the update operation with same all fields.
        """
        # Create valid price detail
        item = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.another_sku.id,
            pricelist_id=self.another_pricelist.id
        )
        await save_object(db_session, item)

        # Try to update to invalid state (same all fields)
        item.price = 100.00
        item.minimum_quantity = 1
        item.sku_id = self.test_sku.id
        item.pricelist_id = self.test_pricelist.id
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_create_item_same_sku_id_pricelist_id_min_qty(
        self, db_session: AsyncSession
    ):
        """
        Test the create operation with same sku_id, pricelist_id, and minimum_quantity.
        """
        duplicate_price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=1,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, duplicate_price_detail)

        await db_session.rollback()

        assert await count_model_objects(db_session, PriceDetails) == 2

    @pytest.mark.asyncio
    async def test_update_item_same_sku_id_pricelist_id_min_qty(
        self, db_session: AsyncSession
    ):
        """
        Test the update operation with same sku_id, pricelist_id, and minimum_quantity.
        """
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.another_sku.id,
            pricelist_id=self.another_pricelist.id
        )
        await save_object(db_session, price_detail)

        price_detail.sku_id = self.test_sku.id
        price_detail.pricelist_id = self.test_pricelist.id
        price_detail.minimum_quantity = 1
        with pytest.raises(IntegrityError):
            await save_object(db_session, price_detail)

        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_create_item_same_sku_id_pricelist_id(
        self, db_session: AsyncSession
    ):
        """
        Test the create operation with same sku_id, pricelist_id.
        """
        duplicate_price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )

        await save_object(db_session, duplicate_price_detail)

        assert await count_model_objects(db_session, PriceDetails) == 3

    @pytest.mark.asyncio
    async def test_update_item_same_sku_id_pricelist_id(
        self, db_session: AsyncSession
    ):
        """
        Test the update operation with same sku_id, pricelist_id.
        """
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.another_sku.id,
            pricelist_id=self.another_pricelist.id
        )

        await save_object(db_session, price_detail)
        assert price_detail.sku_id == self.another_sku.id
        assert price_detail.sku == self.another_sku
        assert price_detail.sku.name == "Another SKU"

        assert price_detail.pricelist_id == self.another_pricelist.id
        assert price_detail.pricelist == self.another_pricelist
        assert price_detail.pricelist.name == "Another Pricelist"

        price_detail.sku_id = self.test_sku.id
        price_detail.pricelist_id = self.test_pricelist.id
        await save_object(db_session, price_detail)

        assert price_detail.sku_id == self.test_sku.id
        assert price_detail.sku == self.test_sku
        assert price_detail.sku.name == "Test SKU"

        assert price_detail.pricelist_id == self.test_pricelist.id
        assert price_detail.pricelist == self.test_pricelist
        assert price_detail.pricelist.name == "Test Pricelist"

    @pytest.mark.asyncio
    async def test_create_item_same_sku_id_min_qty(
        self, db_session: AsyncSession
    ):
        """
        Test the create operation with same sku_id, minimum_quantity.
        """
        duplicate_price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=1,
            sku_id=self.test_sku.id,
            pricelist_id=self.another_pricelist.id
        )
        await save_object(db_session, duplicate_price_detail)
        assert await count_model_objects(db_session, PriceDetails) == 3

    @pytest.mark.asyncio
    async def test_update_item_same_sku_id_min_qty(
        self, db_session: AsyncSession
    ):
        """
        Test the update operation with same sku_id, minimum_quantity.
        """
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.another_sku.id,
            pricelist_id=self.another_pricelist.id
        )
        await save_object(db_session, price_detail)
        assert price_detail.sku_id == self.another_sku.id
        assert price_detail.sku == self.another_sku
        assert price_detail.sku.name == "Another SKU"
        assert price_detail.minimum_quantity == 3

        price_detail.sku_id = self.test_sku.id
        price_detail.minimum_quantity = 1
        await save_object(db_session, price_detail)
        assert price_detail.sku_id == self.test_sku.id
        assert price_detail.sku == self.test_sku
        assert price_detail.sku.name == "Test SKU"
        assert price_detail.minimum_quantity == 1

    @pytest.mark.asyncio
    async def test_create_item_same_pricelist_id_min_qty(
        self, db_session: AsyncSession
    ):
        """
        Test the create operation with same pricelist_id, minimum_quantity.
        """
        duplicate_price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=1,
            sku_id=self.another_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        await save_object(db_session, duplicate_price_detail)
        assert await count_model_objects(db_session, PriceDetails) == 3

    @pytest.mark.asyncio
    async def test_update_item_same_pricelist_id_min_qty(
        self, db_session: AsyncSession
    ):
        """
        Test the update operation with same pricelist_id, minimum_quantity.
        """
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.another_sku.id,
            pricelist_id=self.another_pricelist.id
        )
        await save_object(db_session, price_detail)
        assert price_detail.pricelist_id == self.another_pricelist.id
        assert price_detail.pricelist == self.another_pricelist
        assert price_detail.pricelist.name == "Another Pricelist"
        assert price_detail.minimum_quantity == 3

        price_detail.pricelist_id = self.test_pricelist.id
        price_detail.minimum_quantity = 1
        await save_object(db_session, price_detail)
        assert price_detail.pricelist_id == self.test_pricelist.id
        assert price_detail.pricelist == self.test_pricelist
        assert price_detail.pricelist.name == "Test Pricelist"
        assert price_detail.minimum_quantity == 1

    @pytest.mark.asyncio
    async def test_create_item_same_price_different_min_qty(
        self, db_session: AsyncSession
    ):
        """
        Test the create operation with same price, different minimum_quantity.
        """
        duplicate_price_detail = PriceDetails(
            price=100.00,
            minimum_quantity=5,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        await save_object(db_session, duplicate_price_detail)
        assert await count_model_objects(db_session, PriceDetails) == 3

    @pytest.mark.asyncio
    async def test_update_item_same_price_different_min_qty(
        self, db_session: AsyncSession
    ):
        """
        Test the update operation with same price, different minimum_quantity.
        """
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.another_sku.id,
            pricelist_id=self.another_pricelist.id
        )
        await save_object(db_session, price_detail)
        assert price_detail.price == 300.00
        assert price_detail.minimum_quantity == 3

        price_detail.price = 100.00
        price_detail.minimum_quantity = 1
        await save_object(db_session, price_detail)
        assert price_detail.price == 100.00
        assert price_detail.minimum_quantity == 1


class TestPriceDetailSkuRelationship:
    """Test suite for PriceDetail model relationships with Sku model"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_price_details):
        """Setup method for the test suite"""
        self.test_sku, self.test_pricelist, self.test_price_detail1, \
            self.test_price_detail2 = setup_price_details

    @pytest.mark.asyncio
    async def test_price_detail_with_sku_relationship(self, db_session: AsyncSession):
        """Test the price detail with sku relationship"""
        retrieved_price_detail = await get_object_by_id(
            db_session,
            PriceDetails,
            self.test_price_detail1.id
        )

        assert retrieved_price_detail.sku_id == self.test_sku.id
        assert retrieved_price_detail.sku == self.test_sku
        assert retrieved_price_detail.sku.name == "Test SKU"

    @pytest.mark.asyncio
    async def test_price_detail_without_sku_relationship(
        self, db_session: AsyncSession
    ):
        """Test the price detail without sku relationship"""
        item = PriceDetails(
            price=100.00,
            minimum_quantity=1,
            pricelist_id=self.test_pricelist.id
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_price_detail_to_different_sku(
        self, db_session: AsyncSession, sku_factory
    ):
        """Test the update price detail to different sku"""
        another_sku = await sku_factory(name="Another SKU")
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        await save_object(db_session, price_detail)

        assert price_detail.sku_id == self.test_sku.id
        assert price_detail.sku == self.test_sku
        assert price_detail.sku.name == "Test SKU"

        price_detail.sku_id = another_sku.id
        await save_object(db_session, price_detail)

        assert price_detail.sku_id == another_sku.id
        assert price_detail.sku == another_sku
        assert price_detail.sku.name == "Another SKU"

    @pytest.mark.asyncio
    async def test_create_price_detail_with_invalid_sku_id(
        self, db_session: AsyncSession
    ):
        """Test the create price detail with invalid sku_id"""
        item = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=999,
            pricelist_id=self.test_pricelist.id
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_price_detail_with_invalid_sku_id(
        self, db_session: AsyncSession
    ):
        """Test the update price detail with invalid sku_id"""
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        await save_object(db_session, price_detail)

        price_detail.sku_id = 999
        with pytest.raises(IntegrityError):
            await save_object(db_session, price_detail)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_setting_sku_id_to_null_fails(self, db_session: AsyncSession):
        """Test the setting sku_id to null fails"""
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        await save_object(db_session, price_detail)
        price_detail.sku_id = None
        with pytest.raises(IntegrityError):
            await save_object(db_session, price_detail)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_price_detail_with_sku_relationship(
        self, db_session: AsyncSession
    ):
        """Test the delete price detail with sku relationship"""
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        await save_object(db_session, price_detail)

        sku = await get_object_by_id(
            db_session,
            Skus,
            self.test_sku.id
        )
        await db_session.refresh(sku, ['price_details'])

        assert sku.price_details == [
            self.test_price_detail1,
            self.test_price_detail2,
            price_detail
        ]

        await delete_object(db_session, price_detail)

        deleted_price_detail = await get_object_by_id(
            db_session,
            PriceDetails,
            price_detail.id
        )
        assert deleted_price_detail is None

        await db_session.refresh(sku, ['price_details'])
        assert sku is not None
        assert sku.name == "Test SKU"
        assert sku.price_details == [
            self.test_price_detail1,
            self.test_price_detail2
        ]


class TestPriceDetailPricelistRelationship:
    """Test suite for PriceDetail model relationships with Pricelist model"""

    @pytest.fixture(autouse=True)
    def setup_objects(self, setup_price_details):
        """Setup method for the test suite"""
        self.test_sku, self.test_pricelist, self.test_price_detail1, \
            self.test_price_detail2 = setup_price_details

    @pytest.mark.asyncio
    async def test_price_detail_with_pricelist_relationship(
        self, db_session: AsyncSession
    ):
        """Test the price detail with pricelist relationship"""
        retrieved_price_detail = await get_object_by_id(
            db_session,
            PriceDetails,
            self.test_price_detail1.id
        )

        assert retrieved_price_detail.pricelist_id == self.test_pricelist.id
        assert retrieved_price_detail.pricelist == self.test_pricelist
        assert retrieved_price_detail.pricelist.name == "Test Pricelist"

    @pytest.mark.asyncio
    async def test_price_detail_without_pricelist_relationship(
        self, db_session: AsyncSession
    ):
        """Test the price detail without pricelist relationship"""
        item = PriceDetails(
            price=100.00,
            minimum_quantity=1,
            sku_id=self.test_sku.id
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_price_detail_to_different_pricelist(
        self, db_session: AsyncSession, pricelist_factory
    ):
        """Test the update price detail to different pricelist"""
        another_pricelist = await pricelist_factory(name="Another Pricelist")
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        await save_object(db_session, price_detail)

        assert price_detail.pricelist_id == self.test_pricelist.id
        assert price_detail.pricelist == self.test_pricelist
        assert price_detail.pricelist.name == "Test Pricelist"

        price_detail.pricelist_id = another_pricelist.id
        await save_object(db_session, price_detail)

        assert price_detail.pricelist_id == another_pricelist.id
        assert price_detail.pricelist == another_pricelist
        assert price_detail.pricelist.name == "Another Pricelist"

    @pytest.mark.asyncio
    async def test_create_price_detail_with_invalid_pricelist_id(
        self, db_session: AsyncSession
    ):
        """Test the create price detail with invalid pricelist_id"""
        item = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.test_sku.id,
            pricelist_id=999
        )
        with pytest.raises(IntegrityError):
            await save_object(db_session, item)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_price_detail_with_invalid_pricelist_id(
        self, db_session: AsyncSession
    ):
        """Test the update price detail with invalid pricelist_id"""
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        await save_object(db_session, price_detail)

        price_detail.pricelist_id = 999
        with pytest.raises(IntegrityError):
            await save_object(db_session, price_detail)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_setting_pricelist_id_to_null_fails(self, db_session: AsyncSession):
        """Test the setting pricelist_id to null fails"""
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        await save_object(db_session, price_detail)

        price_detail.pricelist_id = None
        with pytest.raises(IntegrityError):
            await save_object(db_session, price_detail)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_price_detail_with_pricelist_relationship(
        self, db_session: AsyncSession
    ):
        """Test the delete price detail with pricelist relationship"""
        price_detail = PriceDetails(
            price=300.00,
            minimum_quantity=3,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist.id
        )
        await save_object(db_session, price_detail)

        pricelist = await get_object_by_id(
            db_session,
            Pricelists,
            self.test_pricelist.id
        )
        await db_session.refresh(pricelist, ['price_details'])

        assert pricelist.price_details == [
            self.test_price_detail1,
            self.test_price_detail2,
            price_detail
        ]

        await delete_object(db_session, price_detail)

        deleted_price_detail = await get_object_by_id(
            db_session,
            PriceDetails,
            price_detail.id
        )
        assert deleted_price_detail is None

        await db_session.refresh(pricelist, ['price_details'])
        assert pricelist is not None
        assert pricelist.name == "Test Pricelist"
        assert pricelist.price_details == [
            self.test_price_detail1,
            self.test_price_detail2
        ]
