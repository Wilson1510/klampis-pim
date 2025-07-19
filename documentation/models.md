# Entity Relationships
Base model:
```
┌─────────────────┐
│      Base       │
│─────────────────│
│ id (PK)         │
│ created_at      │
│ updated_at      │
│ created_by      │
│ updated_by      │
│ is_active       │
│ sequence        │
└─────────────────┘
```
This model will be inherited to all models in the ERD structure except Users

ERD structure:

```
┌─────────────────┐
│      Users      │
│─────────────────│
│ id (PK)         │
│ username        │
│ password        │
│ name            │
│ role            │
│ created_at      │
│ updated_at      │
│ created_by      │
│ updated_by      │
│ is_active       │
│ sequence        │
└─────────────────┘

┌─────────────────┐    1:N    ┌─────────────────┐    1:N    ┌─────────────────┐    N:1    ┌─────────────────┐
│  CategoryTypes  │◄──────────│   Categories    │◄──────────│    Products     │──────────►│    Suppliers    │
│─────────────────│           │─────────────────│           │─────────────────│           │─────────────────│
│ id (PK)         │           │ id (PK)         │           │ id (PK)         │           │ id (PK)         │
│ name            │           │ name            │           │ name            │           │ name            │
│ slug            │           │ slug            │           │ slug            │           │ slug            │
│ created_at      │           │ description     │           │ description     │           │ company_type    │
│ updated_at      │           │category_type_id │           │ category_id (FK)│           │ address         │
│ created_by (FK) │           │     (FK)        │           │ supplier_id (FK)│           │ contact         │
│ updated_by (FK) │           │ parent_id (FK)  │           │ created_at      │           │ email           │
│ is_active       │           │ created_at      │           │ updated_at      │           │ created_at      │
│ sequence        │           │ updated_at      │           │ created_by (FK) │           │ updated_at      │
└─────────────────┘           │ created_by (FK) │           │ updated_by (FK) │           │ created_by (FK) │
                              │ updated_by (FK) │           │ is_active       │           │ updated_by (FK) │
                              │ is_active       │           │ sequence        │           │ is_active       │
                              │ sequence        │           └─────────────────┘           │ sequence        │
                              └─────────────────┘                          │              └─────────────────┘
                                       │                                   │ 1:N
                                       │ 1:N (self-referencing)            ▼
                                       ▼                          ┌─────────────────┐
                              ┌─────────────────┐                 │      Skus       │
                              │   Categories    │                 │─────────────────│
                              │   (children)    │                 │ id (PK)         │
                              │─────────────────│                 │ name            │
                              │ parent_id (FK)  │                 │ slug            │
                              └─────────────────┘                 │ description     │
                                                                  │ sku_number      │
                                                                  │ product_id (FK) │
                                                                  │ created_at      │
                                                                  │ updated_at      │
                                                                  │ created_by (FK) │
                                                                  │ updated_by (FK) │
                                                                  │ is_active       │
                                                                  │ sequence        │
                                                                  └─────────────────┘
                                                                     │
                                                                     │ 1:N
                                                                     ▼
                                                            ┌─────────────────┐
                                                            │  PriceDetails   │
                                                            │─────────────────│
                                                            │ id (PK)         │
                                                            │ price           │
                                                            │ minimum_quantity│
                                                            │ sku_id (FK)     │
                                                            │ pricelist_id(FK)│
                                                            │ created_at      │
                                                            │ updated_at      │
                                                            │ created_by (FK) │
                                                            │ updated_by (FK) │
                                                            │ is_active       │
                                                            │ sequence        │
                                                            └─────────────────┘
                                                                     ▲
                                                                     │ 1:N
                                                            ┌─────────────────┐
                                                            │   Pricelists    │
                                                            │─────────────────│
                                                            │ id (PK)         │
                                                            │ name            │
                                                            │ code            │
                                                            │ description     │
                                                            │ created_at      │
                                                            │ updated_at      │
                                                            │ created_by (FK) │
                                                            │ updated_by (FK) │
                                                            │ is_active       │
                                                            │ sequence        │
                                                            └─────────────────┘


# Attribute Management System

┌─────────────────┐    M:N    ┌─────────────────┐    M:N    ┌─────────────────┐
│   Categories    │◄──────────│CategoryAttribute│──────────►│ AttributeSets   │
│─────────────────│           │     Set         │           │─────────────────│
│ id (PK)         │           │─────────────────│           │ id (PK)         │
│ name            │           │ category_id (FK)│           │ name            │
│ slug            │           │attribute_set_id │           │ created_at      │
│ description     │           │       (FK)      │           │ updated_at      │
│ ...             │           └─────────────────┘           │ created_by (FK) │
└─────────────────┘                                         │ updated_by (FK) │
                                                            │ is_active       │
                                                            │ sequence        │
                                                            └─────────────────┘
                                                                     │
                                                                     │ M:N
                                                                     ▼
                                                            ┌─────────────────┐
                                                            │AttributeSet     │
                                                            │   Attribute     │
                                                            │─────────────────│
                                                            │ attribute_set_id│
                                                            │       (FK)      │
                                                            │ attribute_id(FK)│
                                                            └─────────────────┘
                                                                     ▲
                                                                     │ M:N
                                                            ┌─────────────────┐
                                                            │   Attributes    │
                                                            │─────────────────│
                                                            │ id (PK)         │
                                                            │ name            │
                                                            │ code            │
                                                            │ data_type       │
                                                            │ uom             │
                                                            │ created_at      │
                                                            │ updated_at      │
                                                            │ created_by (FK) │
                                                            │ updated_by (FK) │
                                                            │ is_active       │
                                                            │ sequence        │
                                                            └─────────────────┘
                                                                     │
                                                                     │
                                                                     ▼
                                                            ┌─────────────────┐
                                                            │SkuAttributeValue│
                                                            │─────────────────│
                                                            │ id (PK)         │
                                                            │ sku_id (FK)     │
                                                            │ attribute_id(FK)│
                                                            │ value           │
                                                            │ created_at      │
                                                            │ updated_at      │
                                                            │ created_by (FK) │
                                                            │ updated_by (FK) │
                                                            │ is_active       │
                                                            │ sequence        │
                                                            └─────────────────┘
                                                                     ▲
                                                                     │
                                                            ┌─────────────────┐
                                                            │      Skus       │
                                                            │─────────────────│
                                                            │ id (PK)         │
                                                            │ name            │
                                                            │ slug            │
                                                            │ description     │
                                                            │ sku_number      │
                                                            │ product_id (FK) │
                                                            │ ...             │
                                                            └─────────────────┘

┌─────────────────┐    Generic FK    ┌─────────────────┐
│     Images      │◄─────────────────│   Products      │
│─────────────────│                  │      Skus       │
│ id (PK)         │                  │─────────────────│
│ file            │                  │ content_type    │
│ title           │                  │ object_id       │
│ is_primary      │                  └─────────────────┘
│ content_type    │
│ object_id       │
│ created_at      │
│ updated_at      │
│ created_by (FK) │
│ updated_by (FK) │
│ is_active       │
│ sequence        │
└─────────────────┘
```

# Key Relationships Summary:
- **User** → **All Models** (created_by, updated_by)
- **CategoryTypes** → **Categories** (1:N via category_type_id)
- **Categories** → **Categories** (1:N self-referencing via parent_id)
- **Categories** → **Products** (1:N)
- **Products** → **Skus** (1:N)
- **Categories** ↔ **AttributeSets** (M:N via CategoryAttributeSet)
- **AttributeSets** ↔ **Attributes** (M:N via AttributeSetAttribute)
- **Skus** ↔ **Attributes** (M:N via SkuAttributeValue with value data)
- **Suppliers** → **Products** (1:N)
- **Skus** → **PriceDetails** (1:N)
- **Pricelists** → **PriceDetails** (1:N)
- **Images** → **Products/Skus** (Generic Foreign Key)

# Attribute System Explanation:

## 1. Category ↔ AttributeSet (M:N)
- **Categories** can use multiple **AttributeSets** as templates
- **AttributeSets** can be used by multiple **Categories**
- Junction table: **CategoryAttributeSet**

## 2. AttributeSet ↔ Attribute (M:N)
- **AttributeSets** contain collections of **Attributes**
- **Attributes** can be part of multiple **AttributeSets**
- Junction table: **AttributeSetAttribute**

## 3. Sku ← SkuAttributeValue → Attribute (Association Object)
- **Skus** have many **SkuAttributeValue** records
- **Attributes** are connected to many **SkuAttributeValue** records
- **SkuAttributeValue** stores the specific value of an attribute for a SKU
- This is a Many-to-Many relationship with additional data (value)