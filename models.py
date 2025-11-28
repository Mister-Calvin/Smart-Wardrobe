from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRESQL_KEY = os.getenv("POSTGRESQL_KEY")
engine = create_engine(POSTGRESQL_KEY)

Base = declarative_base() #Das ist die Grundlage, aus der SQLAlchemy später Tabellen erzeugt.


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

#Base.metadata.create_all(engine) #tabelle erstellen

Session = sessionmaker(bind=engine, autoflush=False)  #Session = Verbindung zur Datenbank
session = Session()

if __name__ == "__main__":
    new_item = Wardrobe(
        name='jetzt gehts',
        category='einfach'
    )

    session.add(new_item)
    session.commit()
    print(">>> Test-Item angelegt")

