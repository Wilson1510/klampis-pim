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

┌─────────────────┐    1:N    ┌─────────────────┐    1:N    ┌─────────────────┐
│  CategoryTypes  │◄──────────│   Categories    │◄──────────│    Products     │
│─────────────────│           │─────────────────│           │─────────────────│
│ id (PK)         │           │ id (PK)         │           │ id (PK)         │
│ name            │           │ name            │           │ name            │
│ slug            │           │ slug            │           │ slug            │
│ created_at      │           │ description     │           │ description     │
│ updated_at      │           │category_type_id │           │ category_id (FK)│
│ created_by (FK) │           │     (FK)        │           │ supplier_id (FK)│
│ updated_by (FK) │           │ parent_id (FK)  │           │ created_at      │
│ is_active       │           │ created_at      │           │ updated_at      │
│ sequence        │           │ updated_at      │           │ created_by (FK) │
└─────────────────┘           │ created_by (FK) │           │ updated_by (FK) │
                              │ updated_by (FK) │           │ is_active       │
                              │ is_active       │           │ sequence        │
                              │ sequence        │           └─────────────────┘
                              └─────────────────┘                          │
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
                                                                  │ attributes (JSON)│
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

┌─────────────────┐    1:N    ┌─────────────────┐
│    Suppliers    │◄──────────│    Products     │
│─────────────────│           │─────────────────│
│ id (PK)         │           └─────────────────┘
│ name            │
│ slug            │
│ company_type    │
│ address         │
│ contact         │
| email           |
│ created_at      │
│ updated_at      │
│ created_by (FK) │
│ updated_by (FK) │
│ is_active       │
│ sequence        │
└─────────────────┘

┌─────────────────┐    M:N    ┌─────────────────┐    M:N    ┌─────────────────┐
│   Attributes    │◄──────────│Product_Attributes│──────────►│    Products     │
│─────────────────│           │─────────────────│           │─────────────────│
│ id (PK)         │           │ id (PK)         │           └─────────────────┘
│ name            │           │ product_id (FK) │
│ code            │           │ attribute_id(FK)│
│ data_type       │           └─────────────────┘
│ uom             │
│ created_at      │
│ updated_at      │
│ created_by (FK) │
│ updated_by (FK) │
│ is_active       │
│ sequence        │
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
- **Products** ↔ **Attributes** (M:N via Product_Attributes)
- **Suppliers** → **Products** (1:N)
- **Skus** → **PriceDetails** (1:N)
- **Pricelists** → **PriceDetails** (1:N)
- **Images** → **Products/Skus** (Generic Foreign Key)