from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine('sqlite:///wardrobe.db')  #PostgreSQL
Base = declarative_base()


class Wardrobe(Base):
    __tablename__ = 'wardrobe'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    category = Column(String(80))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
        }

    def __repr__(self):
        return f"name:{self.name}, category:{self.category} - id: {self.id}"

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()



new_item = Wardrobe(
    name = 'New Shirt',
    category = 'New category'
)


#session.add(new_item)
#session.commit()

