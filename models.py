from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

POSTGRESQL_KEY = os.getenv("POSTGRESQL_KEY")
engine = create_engine(POSTGRESQL_KEY)

Base = declarative_base() #Grundlage, aus der SQLAlchemy später Tabellen erzeugt


class Wardrobe(Base):
    __tablename__ = 'wardrobe'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(255), nullable=False)
    color = Column(String(255), nullable=False)
    condition = Column(String(255), nullable=False)
    type = Column(String(80))
    score = Column(Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "condition": self.condition,
            "type": self.type,
            "score": self.score
        }

    def __repr__(self):
        return (f"name:{self.name}, description: {self.description}, color: {self.color},"
                f"condition: {self.condition}, type: {self.type}, SCORE: {self.score} - id: {self.id}")

#Base.metadata.create_all(engine) #tabelle erstellen
Session = sessionmaker(bind=engine, autoflush=False)  #Session = Verbindung zur Datenbank
session = Session()





def clear_wardrobe():
    session.query(Wardrobe).delete()
    session.commit()
    print(">>> Datenbank geleert")

#clear_wardrobe()
def create_item():
    items = (
        Wardrobe(name="Schwarzer Hoodie", description="Oversized, Baumwolle", color="schwarz", condition="neu",
                 type="hoodie", score=8),
        Wardrobe(name="Weiße Sneaker", description="Leder, minimalistisch", color="weiß", condition="gut",
                 type="schuhe", score=9),
        Wardrobe(name="Blaue Jeans", description="Slim Fit, Stretch", color="blau", condition="gut", type="hose",
                 score=8),
        Wardrobe(name="Beige Chino", description="Regular Fit, Baumwolle", color="beige", condition="neu", type="hose",
                 score=7),
        Wardrobe(name="Graues T-Shirt", description="Basic, Rundhals", color="grau", condition="gut", type="shirt",
                 score=6),
        Wardrobe(name="Weißes Hemd", description="Oxford, Button-Down", color="weiß", condition="neu", type="hemd",
                 score=8),
        Wardrobe(name="Schwarze Lederjacke", description="Biker-Style", color="schwarz", condition="sehr gut",
                 type="jacke", score=9),
        Wardrobe(name="Dunkelblauer Blazer", description="Ungefüttert, casual", color="dunkelblau", condition="gut",
                 type="blazer", score=8),
        Wardrobe(name="Khaki Parka", description="Wetterfest, Kapuze", color="khaki", condition="gut", type="mantel",
                 score=8),
        Wardrobe(name="Camel Mantel", description="Wolle-Mix, lang", color="camel", condition="sehr gut", type="mantel",
                 score=9),
        Wardrobe(name="Rote Strickmütze", description="Feinstrick, warm", color="rot", condition="neu",
                 type="accessoire", score=6),
        Wardrobe(name="Schwarzer Schal", description="Wolle, weich", color="schwarz", condition="gut",
                 type="accessoire", score=7),
        Wardrobe(name="Brauner Ledergürtel", description="Klassisch, 35mm", color="braun", condition="gut",
                 type="accessoire", score=7),
        Wardrobe(name="Schwarze Uhr", description="Edelstahl, schlicht", color="schwarz", condition="sehr gut",
                 type="accessoire", score=8),
        Wardrobe(name="Sonnenbrille Aviator", description="Metallrahmen", color="gold", condition="gut",
                 type="accessoire", score=7),
        Wardrobe(name="Grauer Cardigan", description="Strick, offen", color="grau", condition="gut", type="strick",
                 score=7),
        Wardrobe(name="Cremefarbener Pullover", description="Kuschelig, Rundhals", color="creme", condition="neu",
                 type="pullover", score=8),
        Wardrobe(name="Schwarzer Rollkragen", description="Feinstrick", color="schwarz", condition="neu",
                 type="pullover", score=8),
        Wardrobe(name="Dunkelgrüner Hoodie", description="Fleece innen", color="dunkelgrün", condition="gut",
                 type="hoodie", score=7),
        Wardrobe(name="Bordeaux Hoodie", description="Oversized, weich", color="bordeaux", condition="gut",
                 type="hoodie", score=7),
        Wardrobe(name="Weiße Bluse", description="Leicht, luftig", color="weiß", condition="gut", type="bluse",
                 score=7),
        Wardrobe(name="Schwarzer Rock", description="Midi, fließend", color="schwarz", condition="neu", type="rock",
                 score=8),
        Wardrobe(name="Jeansrock", description="Mini, Denim", color="blau", condition="gut", type="rock", score=6),
        Wardrobe(name="Schwarzes Kleid", description="Klassisch, knielang", color="schwarz", condition="sehr gut",
                 type="kleid", score=9),
        Wardrobe(name="Blumenkleid", description="Sommerlich, leicht", color="mehrfarbig", condition="gut",
                 type="kleid", score=8),
        Wardrobe(name="Sport-Leggings", description="High-Waist, atmungsaktiv", color="schwarz", condition="gut",
                 type="sport", score=8),
        Wardrobe(name="Jogginghose", description="Relaxed, Baumwolle", color="grau", condition="gut", type="sport",
                 score=7),
        Wardrobe(name="Funktionsshirt", description="Schnelltrocknend", color="blau", condition="neu", type="sport",
                 score=7),
        Wardrobe(name="Windbreaker", description="Leicht, packbar", color="schwarz", condition="gut", type="jacke",
                 score=8),
        Wardrobe(name="Regenjacke", description="Wasserdicht, versiegelte Nähte", color="gelb", condition="gut",
                 type="jacke", score=8),
        Wardrobe(name="Daunenweste", description="Warm, leicht", color="navy", condition="sehr gut", type="weste",
                 score=8),
        Wardrobe(name="Graue Anzughose", description="Tapered, Business", color="grau", condition="gut", type="hose",
                 score=8),
        Wardrobe(name="Weißes Unterhemd", description="Baumwolle, slim", color="weiß", condition="neu",
                 type="unterwäsche", score=5),
        Wardrobe(name="Schwarze Socken", description="5er Pack", color="schwarz", condition="neu", type="unterwäsche",
                 score=5),
        Wardrobe(name="Boxershorts", description="Baumwolle, bequem", color="schwarz", condition="neu",
                 type="unterwäsche", score=6),
        Wardrobe(name="Wollsocken", description="Warm, Wintersocken", color="grau", condition="neu", type="unterwäsche",
                 score=7),
        Wardrobe(name="Schwarze Chelsea Boots", description="Leder, elastisch", color="schwarz", condition="sehr gut",
                 type="schuhe", score=9),
        Wardrobe(name="Braune Boots", description="Derby-Style, robust", color="braun", condition="gut", type="schuhe",
                 score=8),
        Wardrobe(name="Sandalen", description="Sommer, bequem", color="tan", condition="gut", type="schuhe", score=6),
        Wardrobe(name="Laufschuhe", description="Dämpfung, neutral", color="weiß/blau", condition="gut", type="schuhe",
                 score=8),
        Wardrobe(name="Schwarze Cap", description="Baseball Cap", color="schwarz", condition="gut", type="accessoire",
                 score=6),
        Wardrobe(name="Beanie", description="Rippstrick", color="grau", condition="gut", type="accessoire", score=6),
        Wardrobe(name="Rucksack", description="20L, Laptopfach", color="schwarz", condition="gut", type="tasche",
                 score=8),
        Wardrobe(name="Umhängetasche", description="Klein, Lederoptik", color="braun", condition="gut", type="tasche",
                 score=7),
        Wardrobe(name="Tote Bag", description="Canvas, groß", color="natur", condition="gut", type="tasche", score=6),
        Wardrobe(name="Krawatte", description="Schmal, elegant", color="dunkelrot", condition="sehr gut",
                 type="accessoire", score=7),
        Wardrobe(name="Weißes Tanktop", description="Ripp, Basic", color="weiß", condition="gut", type="shirt",
                 score=6),
        Wardrobe(name="Schwarzes Longsleeve", description="Baumwolle, slim", color="schwarz", condition="gut",
                 type="shirt", score=7),
        Wardrobe(name="Karriertes Flanellhemd", description="Weich, Holzfäller-Style", color="rot/schwarz",
                 condition="gut", type="hemd", score=8),
        Wardrobe(name="Grauer Hoodie Zip", description="Mit Reißverschluss", color="grau", condition="gut",
                 type="hoodie", score=7))

    session.add_all(items)
    session.commit()

#create_item()
#clear_wardrobe()


