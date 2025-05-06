from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import validates

from app import db

"""
class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    street_address = Column(String(50))
    description = Column(String(250))

    def __str__(self):
        return self.name

class Review(db.Model):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey('restaurant.id', ondelete="CASCADE"))
    user_name = Column(String(30))
    rating = Column(Integer)
    review_text = Column(String(500))
    review_date = Column(DateTime)

    @validates('rating')
    def validate_rating(self, key, value):
        assert value is None or (1 <= value <= 5)
        return value

    def __str__(self):
        return f"{self.user_name}: {self.review_date:%x}"
"""
# Model for image records
# This model is used to store information about images uploaded by users
# It includes fields for the filename, pixel counts for each color channel,
# the username of the uploader, and a timestamp for when the image was uploaded
class ImageRecord(db.Model):
    __tablename__ = 'image_record'
    id = Column(Integer, primary_key=True)
    filename = Column(String(100), nullable=False)
    pixels_red = Column(Integer, nullable=False)
    pixels_green = Column(Integer, nullable=False)
    pixels_blue = Column(Integer, nullable=False)
    username = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    #url_original = Column(Text)        # opcional: URL donde está subida la imagen
    #urls_converted = Column(Text)     # opcional: JSON/Text con URLs de imágenes procesadas

    def __repr__(self):
        return f"<ImageRecord {self.filename} by {self.username} at {self.timestamp}>"
