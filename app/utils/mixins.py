from sqlalchemy import and_
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.ext.declarative import declared_attr


class Imageable:
    """
    Mixin for adding polymorphic 'images' relationship to a model.
    """
    @declared_attr
    def images(cls):
        # Import Image inside function to avoid circular import
        from app.models.image_model import Images

        # Define one-to-many relationship
        return relationship(
            "Images",
            primaryjoin=lambda: and_(
                cls.id == foreign(Images.object_id),
                Images.content_type == cls.__tablename__
            ),
            cascade="all, delete-orphan",
            overlaps="images"
        )
