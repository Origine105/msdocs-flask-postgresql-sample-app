from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import validates

from app import db

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
