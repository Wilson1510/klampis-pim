"""
Automatic database constraint application using SQLAlchemy events.
This provides fully automatic constraint generation with zero configuration.
"""

from sqlalchemy import event, CheckConstraint, String, Integer, Numeric, Float
from app.core.base import Base


def _apply_automatic_constraints(target, connection, **kw):
    """
    Event listener that automatically applies database constraints
    based on column names and types when table is created.
    """
    print(f"Applying automatic constraints to {target}")
    # Check if target is MetaData (after_create event) or Table
    if hasattr(target, 'tables'):
        # Target is MetaData, iterate through all tables
        for table in target.tables.values():
            _apply_constraints_to_table(table)
    else:
        print("Target is a Table")
        # Target is a Table
        _apply_constraints_to_table(target)


def _apply_constraints_to_table(table):
    """
    Apply automatic constraints to a single table.
    """
    constraints_to_add = []
    table_name = table.name
    
    for column in table.columns:
        column_name = column.name
        column_type = column.type
        
        # Skip system columns
        system_columns = [
            'id', 'created_at', 'updated_at', 'created_by', 
            'updated_by', 'is_active', 'sequence'
        ]
        if column_name in system_columns:
            continue
            
        # Email constraints - auto-detect
        if 'email' in column_name.lower() and isinstance(column_type, String):
            constraints_to_add.extend([
                CheckConstraint(
                    f"{column_name} ~ '^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$'",
                    name=f'check_{table_name}_{column_name}_format'
                ),
                CheckConstraint(
                    f"LENGTH({column_name}) >= 5",
                    name=f'check_{table_name}_{column_name}_min_length'
                ),
                CheckConstraint(
                    f"LENGTH({column_name}) <= 100",
                    name=f'check_{table_name}_{column_name}_max_length'
                )
            ])
        
        # Phone/contact constraints - auto-detect
        phone_patterns = ['contact', 'phone', 'mobile', 'telp', 'whatsapp']
        phone_match = any(pattern in column_name.lower() for pattern in phone_patterns)
        if phone_match and isinstance(column_type, String):
            constraints_to_add.extend([
                CheckConstraint(
                    f"{column_name} ~ '^[0-9]+$'",
                    name=f'check_{table_name}_{column_name}_digits_only'
                ),
                CheckConstraint(
                    f"LENGTH({column_name}) >= 8",
                    name=f'check_{table_name}_{column_name}_min_length'
                ),
                CheckConstraint(
                    f"LENGTH({column_name}) <= 15",
                    name=f'check_{table_name}_{column_name}_max_length'
                )
            ])
        
        # Name constraints - auto-detect
        if column_name.lower() == 'name' and isinstance(column_type, String):
            constraints_to_add.extend([
                CheckConstraint(
                    f"LENGTH(TRIM({column_name})) > 0",
                    name=f'check_{table_name}_{column_name}_not_empty'
                ),
                CheckConstraint(
                    f"LENGTH({column_name}) <= 100",
                    name=f'check_{table_name}_{column_name}_max_length'
                ),
                CheckConstraint(
                    f"{column_name} ~ '^[A-Za-z].*'",
                    name=f'check_{table_name}_{column_name}_starts_with_letter'
                )
            ])
        
        # Slug constraints - auto-detect
        if column_name.lower() == 'slug' and isinstance(column_type, String):
            constraints_to_add.extend([
                CheckConstraint(
                    f"LENGTH(TRIM({column_name})) > 0",
                    name=f'check_{table_name}_{column_name}_not_empty'
                ),
                CheckConstraint(
                    f"{column_name} ~ '^[a-z0-9-]+$'",
                    name=f'check_{table_name}_{column_name}_format'
                ),
                CheckConstraint(
                    f"LENGTH({column_name}) <= 100",
                    name=f'check_{table_name}_{column_name}_max_length'
                )
            ])
        
        # Code constraints - auto-detect
        if column_name.lower() == 'code' and isinstance(column_type, String):
            constraints_to_add.extend([
                CheckConstraint(
                    f"LENGTH(TRIM({column_name})) > 0",
                    name=f'check_{table_name}_{column_name}_not_empty'
                ),
                CheckConstraint(
                    f"{column_name} ~ '^[A-Z0-9_-]+$'",
                    name=f'check_{table_name}_{column_name}_format'
                ),
                CheckConstraint(
                    f"LENGTH({column_name}) <= 50",
                    name=f'check_{table_name}_{column_name}_max_length'
                )
            ])
        
        # Positive number constraints - auto-detect
        positive_patterns = [
            'price', 'quantity', 'amount', 'cost', 'total', 'minimum_', 'maximum_'
        ]
        positive_match = any(
            pattern in column_name.lower() for pattern in positive_patterns
        )
        if positive_match and isinstance(column_type, (Integer, Numeric, Float)):
            constraints_to_add.append(
                CheckConstraint(
                    f"{column_name} > 0",
                    name=f'check_{table_name}_{column_name}_positive'
                )
            )
        
        # Username constraints - auto-detect
        if column_name.lower() == 'username' and isinstance(column_type, String):
            constraints_to_add.extend([
                CheckConstraint(
                    f"LENGTH(TRIM({column_name})) > 0",
                    name=f'check_{table_name}_{column_name}_not_empty'
                ),
                CheckConstraint(
                    f"LENGTH({column_name}) >= 3",
                    name=f'check_{table_name}_{column_name}_min_length'
                ),
                CheckConstraint(
                    f"LENGTH({column_name}) <= 20",
                    name=f'check_{table_name}_{column_name}_max_length'
                ),
                CheckConstraint(
                    f"{column_name} ~ '^[a-zA-Z0-9_]+$'",
                    name=f'check_{table_name}_{column_name}_format'
                )
            ])
        
        # SKU number constraints - auto-detect
        sku_match = 'sku' in column_name.lower() and 'number' in column_name.lower()
        if sku_match and isinstance(column_type, String):
            constraints_to_add.extend([
                CheckConstraint(
                    f"LENGTH({column_name}) = 10",
                    name=f'check_{table_name}_{column_name}_length'
                ),
                CheckConstraint(
                    f"{column_name} ~ '^[0-9A-F]{{10}}$'",
                    name=f'check_{table_name}_{column_name}_format'
                )
            ])
        
        # Description/Text field constraints - auto-detect
        description_patterns = [
            'description', 'desc', 'note', 'notes', 'comment', 'comments'
        ]
        desc_match = any(
            pattern in column_name.lower() for pattern in description_patterns
        )
        if desc_match and isinstance(column_type, String):
            # Only add max length constraint for description fields
            if hasattr(column_type, 'length') and column_type.length:
                constraints_to_add.append(
                    CheckConstraint(
                        f"LENGTH({column_name}) <= {column_type.length}",
                        name=f'check_{table_name}_{column_name}_max_length'
                    )
                )
    
    # Add all constraints to the table
    for constraint in constraints_to_add:
        # Check if constraint with same name already exists
        existing_names = [
            c.name for c in table.constraints 
            if hasattr(c, 'name') and c.name
        ]
        if constraint.name not in existing_names:
            table.append_constraint(constraint)


def _apply_automatic_constraints_after_configured(mapper, cls):
    """
    Event listener that runs after mapper is configured.
    This ensures we can access the table after it's fully created.
    """
    print(f"Applying constraints to {cls} after mapper is configured")
    if hasattr(cls, '__table__') and cls.__table__ is not None:
        # Apply constraints to the table
        _apply_constraints_to_table(cls.__table__)


def register_constraint_listeners():
    """
    Register automatic constraint listeners.
    Call this function once during application startup.
    """
    print("Registering constraint listeners")
    # Listen for table creation events
    event.listen(
        Base.metadata,
        'before_create',
        _apply_automatic_constraints,
        propagate=True
    )
    
    # Listen for mapper configuration events
    event.listen(
        Base,
        'mapper_configured',
        _apply_automatic_constraints_after_configured,
        propagate=True
    )


def apply_constraints_to_existing_models():
    """
    Apply constraints to all existing models.
    This can be called after all models are imported.
    """
    print("Applying constraints to existing models")
    for cls in Base.registry._class_registry.values():
        if hasattr(cls, '__table__') and cls.__table__ is not None:
            _apply_constraints_to_table(cls.__table__) 