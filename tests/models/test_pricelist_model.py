from sqlalchemy import String, event, select, Text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import pytest

from app.core.base import Base
from app.models import Pricelists, PriceDetails
from app.core.listeners import _set_code
from tests.utils.model_test_utils import (
    save_object,
    get_object_by_id,
    get_all_objects,
    delete_object,
    count_model_objects,
    assert_relationship
)


@pytest.fixture
async def setup_pricelists(pricelist_factory):
    """
    Fixture to create pricelists ONCE for the entire test module.
    This is the efficient part.
    """
    pricelist1 = await pricelist_factory(name="Test Pricelist 1")
    pricelist2 = await pricelist_factory(name="Test Pricelist 2")
    # Mengembalikan objek-objek yang sudah dibuat
    return pricelist1, pricelist2


class TestPricelist:
    """Test suite for Pricelist model and relationships"""
    @pytest.fixture(autouse=True)
    def setup_class_data(self, setup_pricelists):
        """
        Gets data from the module fixture and injects it into self.
        """
        self.test_pricelist1, self.test_pricelist2 = setup_pricelists

    def test_inheritance_from_base_model(self):
        """Test that Pricelist model inherits from Base model"""
        assert issubclass(Pricelists, Base)

    def test_fields_with_validation(self):
        """Test that Pricelist model has fields with validation"""
        assert not hasattr(Pricelists, 'validate_name')
        assert len(Pricelists.__mapper__.validators) == 0

    def test_has_listeners(self):
        """Test that the model has the expected listeners"""
        assert event.contains(Pricelists.name, 'set', _set_code)
        assert not event.contains(Pricelists, 'set', _set_code)

    def test_name_field_properties(self):
        """Test that the name field has the expected properties"""
        name_column = Pricelists.__table__.columns.get('name')
        assert name_column is not None
        assert isinstance(name_column.type, String)
        assert name_column.type.length == 50
        assert name_column.nullable is False
        assert name_column.unique is None
        assert name_column.index is True
        assert name_column.default is None

    def test_code_field_properties(self):
        """Test that the code field has the expected properties"""
        code_column = Pricelists.__table__.columns.get('code')
        assert code_column is not None
        assert isinstance(code_column.type, String)
        assert code_column.type.length == 50
        assert code_column.nullable is False
        assert code_column.unique is True
        assert code_column.index is True
        assert code_column.default is None

    def test_description_field_properties(self):
        """Test that the description field has the expected properties"""
        description_column = Pricelists.__table__.columns.get('description')
        assert description_column is not None
        assert isinstance(description_column.type, Text)
        assert description_column.nullable is True
        assert description_column.unique is None
        assert description_column.index is None
        assert description_column.default is None

    def test_relationships_with_other_models(self):
        """Test the relationships with other models"""
        assert_relationship(Pricelists, "price_details", "pricelist")

    def test_str_representation(self):
        """Test the string representation"""
        str_repr = str(self.test_pricelist1)
        assert str_repr == "Pricelists(Test Pricelist 1)"

    @pytest.mark.asyncio
    async def test_init_method(self, db_session: AsyncSession):
        """Test the init method"""
        await db_session.refresh(self.test_pricelist1, ['price_details'])
        await db_session.refresh(self.test_pricelist2, ['price_details'])

        assert self.test_pricelist1.id == 1
        assert self.test_pricelist1.name == "Test Pricelist 1"
        assert self.test_pricelist1.code == "TEST-PRICELIST-1"
        assert self.test_pricelist1.description is None
        assert self.test_pricelist1.price_details == []

        assert self.test_pricelist2.id == 2
        assert self.test_pricelist2.name == "Test Pricelist 2"
        assert self.test_pricelist2.code == "TEST-PRICELIST-2"
        assert self.test_pricelist2.description is None
        assert self.test_pricelist2.price_details == []

    @pytest.mark.asyncio
    async def test_create_operation(self, db_session: AsyncSession):
        """Test the create operation"""
        item = Pricelists(name="Test Pricelist 3")
        await save_object(db_session, item)

        assert item.id == 3
        assert item.name == "Test Pricelist 3"
        assert item.code == "TEST-PRICELIST-3"
        assert item.description is None
        assert await count_model_objects(db_session, Pricelists) == 3

        item_with_code = Pricelists(
            name="Test Pricelist 4",
            code="code-pricelist-4"
        )
        await save_object(db_session, item_with_code)
        assert item_with_code.id == 4
        assert item_with_code.name == "Test Pricelist 4"
        # code should be set to the slugified name
        assert item_with_code.code == "TEST-PRICELIST-4"
        assert item_with_code.description is None
        assert await count_model_objects(db_session, Pricelists) == 4

    @pytest.mark.asyncio
    async def test_get_operation(self, db_session: AsyncSession):
        """Test the get operation"""
        item = await get_object_by_id(
            db_session,
            Pricelists,
            self.test_pricelist1.id
        )
        assert item.id == 1
        assert item.name == "Test Pricelist 1"
        assert item.code == "TEST-PRICELIST-1"

        item = await get_object_by_id(
            db_session,
            Pricelists,
            self.test_pricelist2.id
        )

        assert item.id == 2
        assert item.name == "Test Pricelist 2"
        assert item.code == "TEST-PRICELIST-2"

        items = await get_all_objects(db_session, Pricelists)
        assert len(items) == 2
        assert items[0].id == 1
        assert items[0].name == "Test Pricelist 1"
        assert items[0].code == "TEST-PRICELIST-1"
        assert items[0].description is None

        assert items[1].id == 2
        assert items[1].name == "Test Pricelist 2"
        assert items[1].code == "TEST-PRICELIST-2"
        assert items[1].description is None

    @pytest.mark.asyncio
    async def test_update_operation(self, db_session: AsyncSession):
        """Test the update operation"""
        item = await get_object_by_id(
            db_session,
            Pricelists,
            self.test_pricelist1.id
        )
        item.name = "updated test pricelist 1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test pricelist 1"
        assert item.code == "UPDATED-TEST-PRICELIST-1"
        assert item.description is None
        assert await count_model_objects(db_session, Pricelists) == 2

        item.code = "updated-code-pricelist-1"
        await save_object(db_session, item)

        assert item.id == 1
        assert item.name == "updated test pricelist 1"
        # code should be set to the slugified name
        assert item.code == "UPDATED-TEST-PRICELIST-1"
        assert await count_model_objects(db_session, Pricelists) == 2

    @pytest.mark.asyncio
    async def test_delete_operation(self, db_session: AsyncSession):
        """Test the delete operation"""
        await delete_object(db_session, self.test_pricelist1)

        item = await get_object_by_id(
            db_session,
            Pricelists,
            self.test_pricelist1.id
        )
        assert item is None
        assert await count_model_objects(db_session, Pricelists) == 1


class TestPricelistPriceDetailRelationship:
    """Test suite for Pricelist model relationships with PriceDetail model"""

    @pytest.fixture(autouse=True)
    async def setup_class_data(self, setup_pricelists, sku_factory):
        """
        Gets data from the module fixture and injects it into self.
        """
        self.test_pricelist1, self.test_pricelist2 = setup_pricelists
        self.test_sku = await sku_factory(name="Test Sku")

    @pytest.mark.asyncio
    async def test_create_pricelist_with_price_detail(self, db_session: AsyncSession):
        """Test creating a pricelist with a price detail"""
        pricelist = Pricelists(
            name="Test Pricelist 3",
            price_details=[
                PriceDetails(
                    price=100.00,
                    minimum_quantity=1,
                    sku_id=self.test_sku.id
                ),
                PriceDetails(
                    price=200.00,
                    minimum_quantity=2,
                    sku_id=self.test_sku.id
                )
            ]
        )
        await save_object(db_session, pricelist)

        retrieved_pricelist = await get_object_by_id(
            db_session,
            Pricelists,
            pricelist.id
        )
        await db_session.refresh(retrieved_pricelist, ['price_details'])

        assert retrieved_pricelist.id == 3
        assert retrieved_pricelist.name == "Test Pricelist 3"
        assert retrieved_pricelist.code == "TEST-PRICELIST-3"
        assert retrieved_pricelist.description is None
        assert len(retrieved_pricelist.price_details) == 2

        assert retrieved_pricelist.price_details[0].id == 1
        assert retrieved_pricelist.price_details[0].price == 100.00
        assert retrieved_pricelist.price_details[0].minimum_quantity == 1
        assert retrieved_pricelist.price_details[0].sku_id == self.test_sku.id

        assert retrieved_pricelist.price_details[1].id == 2
        assert retrieved_pricelist.price_details[1].price == 200.00
        assert retrieved_pricelist.price_details[1].minimum_quantity == 2
        assert retrieved_pricelist.price_details[1].sku_id == self.test_sku.id

    @pytest.mark.asyncio
    async def test_add_multiple_price_details_to_pricelist(
        self, db_session: AsyncSession
    ):
        """Test adding multiple price details to a pricelist"""
        for i in range(5):
            price_detail = PriceDetails(
                price=(i + 1) * 100.00,
                minimum_quantity=i + 1,
                sku_id=self.test_sku.id,
                pricelist_id=self.test_pricelist1.id
            )
            await save_object(db_session, price_detail)

        retrieved_pricelist = await get_object_by_id(
            db_session,
            Pricelists,
            self.test_pricelist1.id
        )
        await db_session.refresh(retrieved_pricelist, ['price_details'])

        assert len(retrieved_pricelist.price_details) == 5
        for i in range(5):
            assert retrieved_pricelist.price_details[i].id == i + 1
            assert retrieved_pricelist.price_details[i].price == (i + 1) * 100.00
            assert retrieved_pricelist.price_details[i].minimum_quantity == i + 1
            assert retrieved_pricelist.price_details[i].sku_id == self.test_sku.id

    @pytest.mark.asyncio
    async def test_update_pricelist_price_details(self, db_session: AsyncSession):
        """Test updating a pricelist's price details"""
        pricelist = await get_object_by_id(
            db_session,
            Pricelists,
            self.test_pricelist1.id
        )
        await db_session.refresh(pricelist, ['price_details'])

        assert len(pricelist.price_details) == 0

        pricelist.price_details = [
            PriceDetails(
                price=100.00,
                minimum_quantity=1,
                sku_id=self.test_sku.id
            ),
            PriceDetails(
                price=200.00,
                minimum_quantity=2,
                sku_id=self.test_sku.id
            )
        ]
        await save_object(db_session, pricelist)

        await db_session.refresh(pricelist, ['price_details'])

        assert len(pricelist.price_details) == 2
        assert pricelist.price_details[0].price == 100.00
        assert pricelist.price_details[1].price == 200.00

        pricelist.price_details = [
            PriceDetails(
                price=300.00,
                minimum_quantity=3,
                sku_id=self.test_sku.id
            ),
            PriceDetails(
                price=400.00,
                minimum_quantity=4,
                sku_id=self.test_sku.id
            ),
            PriceDetails(
                price=500.00,
                minimum_quantity=5,
                sku_id=self.test_sku.id
            )
        ]
        # should fail because Test Sku no longer has a pricelist_id
        with pytest.raises(IntegrityError):
            await save_object(db_session, pricelist)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_pricelist_deletion_with_price_details(
        self, db_session: AsyncSession
    ):
        """Test deleting a pricelist that has price details"""

        # Create price details associated with the pricelist
        price_detail = PriceDetails(
            price=100.00,
            minimum_quantity=1,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist1.id
        )
        await save_object(db_session, price_detail)

        # Try to delete pricelist that has associated price details
        with pytest.raises(IntegrityError):
            await delete_object(db_session, self.test_pricelist1)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_orphaned_price_detail_cleanup(self, db_session: AsyncSession):
        """Test handling of price details when their pricelist is deleted"""

        # Create temporary pricelist
        temp_pricelist = Pricelists(name="Temporary Pricelist")
        await save_object(db_session, temp_pricelist)

        # Create price detail associated with temp pricelist
        temp_price_detail = PriceDetails(
            price=100.00,
            sku_id=self.test_sku.id,
            pricelist_id=temp_pricelist.id
        )
        await save_object(db_session, temp_price_detail)

        # Try to delete the pricelist (should fail due to foreign key)
        with pytest.raises(IntegrityError):
            await delete_object(db_session, temp_pricelist)
        await db_session.rollback()

        # To properly delete, first remove the price detail
        await delete_object(db_session, temp_price_detail)

        # Now delete the pricelist
        await delete_object(db_session, temp_pricelist)

        # Verify both are deleted
        deleted_pricelist = await get_object_by_id(
            db_session,
            Pricelists,
            temp_pricelist.id
        )
        deleted_price_detail = await get_object_by_id(
            db_session,
            PriceDetails,
            temp_price_detail.id
        )
        assert deleted_pricelist is None
        assert deleted_price_detail is None

    @pytest.mark.asyncio
    async def test_query_pricelist_by_price_details(self, db_session: AsyncSession):
        """Test querying a pricelist by price details"""

        # Create price details associated with the pricelist
        price_detail = PriceDetails(
            price=100.00,
            minimum_quantity=1,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist1.id
        )
        await save_object(db_session, price_detail)

        price_detail2 = PriceDetails(
            price=200.00,
            minimum_quantity=2,
            sku_id=self.test_sku.id,
            pricelist_id=self.test_pricelist1.id
        )
        await save_object(db_session, price_detail2)

        # Query pricelist by price details
        stmt = select(Pricelists).join(PriceDetails).where(
            PriceDetails.price == 100.00
        )
        result = await db_session.execute(stmt)
        retrieved_pricelist = result.scalar_one_or_none()

        assert retrieved_pricelist.id == self.test_pricelist1.id
        assert retrieved_pricelist.name == "Test Pricelist 1"
        assert retrieved_pricelist.code == "TEST-PRICELIST-1"
