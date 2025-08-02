from sqlalchemy import and_
from sqlalchemy.orm import relationship, foreign
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import validates


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
            overlaps="images",
            cascade="all, delete-orphan"
        )

    @validates('images')
    def validate_image(self, key, image):
        """
        Automatically set content_type when image is added to collection and no
        content_type is provided or is empty string.
        """
        # Only auto-set for None or empty string values
        if (
            image.content_type is None or
            (
                isinstance(image.content_type, str) and
                image.content_type.strip() == ""
            )
        ):
            image.content_type = self.__tablename__
        return image
