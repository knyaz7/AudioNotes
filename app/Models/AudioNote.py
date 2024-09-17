from sqlalchemy import Column, Integer, String, ARRAY, Float
from db import Base


class AudioNote(Base):
    __tablename__ = "audionotes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="")
    description = Column(String, default="")
    tags = Column(ARRAY(String), default=list)
    duration = Column(Float)
    file_path = Column(String, unique=True)