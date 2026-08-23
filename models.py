from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
from pgvector.sqlalchemy import Vector

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
    embedding = Column(Vector(1536), nullable=True)

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

def create_item_colorful_50():
    items = (
        Wardrobe(name="Türkiser Hoodie", description="Oversized, Baumwolle, weiche Innenseite", color="türkis", condition="neu", type="hoodie", score=8),
        Wardrobe(name="Pinkes Basic T-Shirt", description="Rundhals, leicht, everyday", color="pink", condition="neu", type="shirt", score=6),
        Wardrobe(name="Gelbes Longsleeve", description="Baumwolle, slim fit", color="sonnengelb", condition="gut", type="shirt", score=7),
        Wardrobe(name="Korallenrotes Hemd", description="Leinenmix, luftig", color="koralle", condition="sehr gut", type="hemd", score=8),
        Wardrobe(name="Mintgrüne Bluse", description="Fließend, leicht transparent", color="mintgrün", condition="gut", type="bluse", score=7),
        Wardrobe(name="Lila Strickpulli", description="Grobstrick, cozy", color="lila", condition="gut", type="pullover", score=8),
        Wardrobe(name="Orangefarbener Rollkragen", description="Feinstrick, warm", color="orange", condition="neu", type="pullover", score=8),
        Wardrobe(name="Petrolfarbener Cardigan", description="Offen, Strick, weich", color="petrol", condition="gut", type="strick", score=7),
        Wardrobe(name="Bunter Overshirt", description="Kariert, dickes Flanell", color="blau/gelb/weiß", condition="gut", type="hemd", score=8),
        Wardrobe(name="Neon-grünes Funktionsshirt", description="Schnelltrocknend, atmungsaktiv", color="neon-grün", condition="neu", type="sport", score=7),

        Wardrobe(name="Rote Chino", description="Regular Fit, Baumwolle", color="rot", condition="gut", type="hose", score=7),
        Wardrobe(name="Smaragdgrüne Chino", description="Tapered Fit, stretch", color="smaragdgrün", condition="sehr gut", type="hose", score=8),
        Wardrobe(name="Hellblaue Jeans", description="Straight Fit, Denim", color="hellblau", condition="gut", type="hose", score=7),
        Wardrobe(name="Weiße Jeans", description="Slim Fit, clean look", color="weiß", condition="gut", type="hose", score=7),
        Wardrobe(name="Violette Jogginghose", description="Relaxed, Baumwolle", color="violett", condition="gut", type="sport", score=7),
        Wardrobe(name="Türkise Sport-Leggings", description="High-Waist, elastisch", color="türkis", condition="neu", type="sport", score=8),
        Wardrobe(name="Gelber Rock", description="Midi, fließend", color="gelb", condition="gut", type="rock", score=7),
        Wardrobe(name="Kobaltblauer Rock", description="Mini, Denim", color="kobaltblau", condition="gut", type="rock", score=6),
        Wardrobe(name="Fuchsia Kleid", description="Sommerlich, leicht", color="fuchsia", condition="sehr gut", type="kleid", score=8),
        Wardrobe(name="Grünes Kleid", description="Klassisch, knielang", color="waldgrün", condition="gut", type="kleid", score=8),

        Wardrobe(name="Bunte Retro Sneaker", description="Velours/Leder Mix, bequem", color="mehrfarbig", condition="gut", type="schuhe", score=8),
        Wardrobe(name="Gelbe Sneaker", description="Canvas, sommerlich", color="gelb", condition="gut", type="schuhe", score=7),
        Wardrobe(name="Rote High-Top Sneaker", description="Leinen, street", color="rot", condition="gut", type="schuhe", score=7),
        Wardrobe(name="Mintfarbene Laufschuhe", description="Dämpfung, neutral", color="mint/weiß", condition="gut", type="schuhe", score=8),
        Wardrobe(name="Blaue Chelsea Boots", description="Leder, elastisch", color="navy", condition="sehr gut", type="schuhe", score=9),
        Wardrobe(name="Weiße Loafer", description="Minimalistisch, leicht", color="weiß", condition="gut", type="schuhe", score=7),

        Wardrobe(name="Regenjacke in Neonorange", description="Wasserdicht, versiegelte Nähte", color="neonorange", condition="gut", type="jacke", score=8),
        Wardrobe(name="Pinker Windbreaker", description="Leicht, packbar", color="pink", condition="gut", type="jacke", score=7),
        Wardrobe(name="Türkiser Parka", description="Wetterfest, Kapuze", color="türkis", condition="gut", type="mantel", score=8),
        Wardrobe(name="Lila Steppweste", description="Warm, leicht", color="lila", condition="sehr gut", type="weste", score=8),
        Wardrobe(name="Gelber Mantel", description="Wolle-Mix, lang", color="senfgelb", condition="sehr gut", type="mantel", score=9),
        Wardrobe(name="Blauer Blazer", description="Ungefüttert, casual", color="royalblau", condition="gut", type="blazer", score=8),

        Wardrobe(name="Rote Cap", description="Baseball Cap, adjustable", color="rot", condition="gut", type="accessoire", score=6),
        Wardrobe(name="Türkise Beanie", description="Rippstrick, warm", color="türkis", condition="neu", type="accessoire", score=6),
        Wardrobe(name="Gelber Fischerhut", description="Cotton twill, festival", color="gelb", condition="gut", type="headwear", score=6),
        Wardrobe(name="Lilane Strickmütze", description="Feinstrick, weich", color="lila", condition="gut", type="headwear", score=6),

        Wardrobe(name="Regenbogen-Socken", description="3er Pack, bunt, bequem", color="regenbogen", condition="neu", type="socks", score=6),
        Wardrobe(name="Türkise Sportsocken", description="Atmungsaktiv, gepolstert", color="türkis", condition="neu", type="socks", score=6),
        Wardrobe(name="Gelbe Socken", description="Baumwolle, soft", color="gelb", condition="neu", type="socks", score=5),
        Wardrobe(name="Pinke Socken", description="Baumwolle, soft", color="pink", condition="neu", type="socks", score=5),

        Wardrobe(name="Rucksack in Petrol", description="22L, Laptopfach, wasserabweisend", color="petrol", condition="gut", type="bag", score=8),
        Wardrobe(name="Tote Bag in Orange", description="Canvas, groß", color="orange", condition="gut", type="bag", score=6),
        Wardrobe(name="Umhängetasche in Lila", description="Klein, robust, city", color="lila", condition="gut", type="bag", score=7),

        Wardrobe(name="Bunter Schal", description="Wolle-Mix, weich", color="bunt", condition="gut", type="accessory", score=7),
        Wardrobe(name="Gelbe Sonnenbrille", description="Retro-Frame", color="gelb", condition="gut", type="accessory", score=7),
        Wardrobe(name="Roter Ledergürtel", description="Klassisch, 35mm", color="rot", condition="gut", type="accessory", score=7),
        Wardrobe(name="Türkise Uhr", description="Silikonband, sportlich", color="türkis", condition="sehr gut", type="accessory", score=7),
        Wardrobe(name="Statement-Kette", description="Chunky, farbige Elemente", color="mehrfarbig", condition="gut", type="accessory", score=6),
        Wardrobe(name="Bunte Krawatte", description="Schmal, modern", color="blau/pink", condition="sehr gut", type="accessory", score=7),

        Wardrobe(name="Oranges Tanktop", description="Ripp, Basic", color="orange", condition="gut", type="shirt", score=6),
        Wardrobe(name="Türkises Unterhemd", description="Baumwolle, slim", color="türkis", condition="neu", type="unterwäsche", score=5)
    )

    session.add_all(items)
    session.commit()

#create_item_colorful_50()

def create_item_weather_50():
    items = (
        # REGEN (Rain)
        Wardrobe(name="Regenjacke Hardshell (Moosgrün)", description="Wasserdicht (Hardshell), Kapuze, versiegelte Nähte", color="moosgrün", condition="neu", type="jacke", score=9),
        Wardrobe(name="Regenhose (Schwarz)", description="Wasserdicht, überziehbar, verschweißte Nähte", color="schwarz", condition="neu", type="hose", score=8),
        Wardrobe(name="Gummistiefel (Navy)", description="Wasserdicht, rutschfeste Sohle, knöchelhoch", color="navy", condition="sehr gut", type="schuhe", score=8),
        Wardrobe(name="Regenponcho (Neongelb)", description="Ultraleicht, packbar, hoher Kragen", color="neongelb", condition="neu", type="outerwear", score=7),
        Wardrobe(name="Wasserfeste Cap (Schwarz)", description="Water-repellent, gebogener Schirm", color="schwarz", condition="gut", type="headwear", score=6),
        Wardrobe(name="Umbrella Bucket Hat (Petrol)", description="Wasserabweisend, Kordelzug, windstabil", color="petrol", condition="neu", type="headwear", score=7),
        Wardrobe(name="Regen-Overknee-Socken (Grau)", description="Wollmix, schnell trocknend, warm", color="grau", condition="neu", type="socks", score=7),
        Wardrobe(name="Drybag (Orange)", description="Wasserdichter Packsack, Rolltop, 10L", color="orange", condition="neu", type="bag", score=8),

        # SCHNEE (Snow)
        Wardrobe(name="Daunenparka (Schneeweiß)", description="Sehr warm, winddicht, Kapuze", color="schneeweiß", condition="sehr gut", type="mantel", score=9),
        Wardrobe(name="Skijacke (Kobaltblau)", description="Isoliert, Schneefang, wasserdicht", color="kobaltblau", condition="gut", type="jacke", score=9),
        Wardrobe(name="Thermo-Leggings (Schwarz)", description="Fleece innen, eng anliegend, als Layer", color="schwarz", condition="neu", type="bottom", score=8),
        Wardrobe(name="Schneehose (Anthrazit)", description="Wasserabweisend, isoliert, verstärkte Nähte", color="anthrazit", condition="gut", type="hose", score=8),
        Wardrobe(name="Winterstiefel (Braun)", description="Gefüttert, griffige Sohle, wasserabweisend", color="braun", condition="sehr gut", type="schuhe", score=9),
        Wardrobe(name="Schneegamaschen (Schwarz)", description="Hält Schnee/Nässe aus dem Schuh, robust", color="schwarz", condition="neu", type="accessory", score=7),
        Wardrobe(name="Merino-Wollsocken (Bordeaux)", description="Extra warm, geruchshemmend", color="bordeaux", condition="neu", type="socks", score=8),
        Wardrobe(name="Fäustlinge (Rot)", description="Gefüttert, winddicht, wasserabweisend", color="rot", condition="neu", type="accessory", score=8),

        # WIND (Wind)
        Wardrobe(name="Windbreaker (Türkis)", description="Winddicht, leicht, packbar", color="türkis", condition="gut", type="jacke", score=8),
        Wardrobe(name="Softshell-Jacke (Grau)", description="Windstopper, leicht wasserabweisend, elastisch", color="grau", condition="sehr gut", type="jacke", score=8),
        Wardrobe(name="Winddichte Laufweste (Neonpink)", description="Front winddicht, Rücken atmungsaktiv", color="neonpink", condition="neu", type="weste", score=7),
        Wardrobe(name="Windproof Beanie (Schwarz)", description="Innenfleece, winddichte Front", color="schwarz", condition="neu", type="headwear", score=7),
        Wardrobe(name="Multifunktionstuch (Violett)", description="Neck gaiter, wind- & kälteschutz", color="violett", condition="neu", type="accessory", score=7),
        Wardrobe(name="Windfeste Handschuhe (Schwarz)", description="Dünn, griffig, touchscreenfähig", color="schwarz", condition="neu", type="accessory", score=7),
        Wardrobe(name="Sturmhaube (Dunkelblau)", description="Atmungsaktiv, winddicht, unter Helm", color="dunkelblau", condition="neu", type="headwear", score=7),
        Wardrobe(name="Windfester Schal (Camel)", description="Wolle-Mix, dicht gewebt", color="camel", condition="gut", type="accessory", score=7),

        # KÄLTE (Cold)
        Wardrobe(name="Thermo-Unterhemd (Schwarz)", description="Base Layer, warm, schnelltrocknend", color="schwarz", condition="neu", type="top", score=8),
        Wardrobe(name="Merino-Longsleeve (Tannengrün)", description="Wärmt, kratzt nicht, als Base Layer", color="tannengrün", condition="neu", type="top", score=9),
        Wardrobe(name="Fleecejacke (Orange)", description="Midlayer, weich, warm", color="orange", condition="gut", type="outerwear", score=8),
        Wardrobe(name="Strickpulli Grob (Senfgelb)", description="Sehr warm, grober Strick", color="senfgelb", condition="gut", type="top", score=8),
        Wardrobe(name="Steppweste (Petrol)", description="Isoliert, leicht, Layering", color="petrol", condition="sehr gut", type="outerwear", score=8),
        Wardrobe(name="Thermo-Chino (Navy)", description="Gefüttert, wintertauglich, clean", color="navy", condition="gut", type="bottom", score=8),
        Wardrobe(name="Wintermütze (Weinrot)", description="Rippstrick, sehr warm", color="weinrot", condition="neu", type="headwear", score=7),
        Wardrobe(name="Wollschal XXL (Grau)", description="Groß, warm, weich", color="grau", condition="sehr gut", type="accessory", score=8),

        # HITZE (Heat)
        Wardrobe(name="Leinenhemd Kurzarm (Weiß)", description="Sehr luftig, Sommer", color="weiß", condition="neu", type="top", score=8),
        Wardrobe(name="Leinenhose (Sand)", description="Atmungsaktiv, locker, sommerlich", color="sand", condition="neu", type="bottom", score=8),
        Wardrobe(name="Sommer-Shorts (Mint)", description="Leicht, relaxed fit", color="mint", condition="gut", type="bottom", score=7),
        Wardrobe(name="Sport-Top Mesh (Neongrün)", description="Sehr atmungsaktiv, schnelltrocknend", color="neongrün", condition="neu", type="top", score=7),
        Wardrobe(name="Sonnenhut (Beige)", description="Breite Krempe, UV-Schutz", color="beige", condition="neu", type="headwear", score=8),
        Wardrobe(name="Sonnenbrille Sport (Schwarz)", description="UV400, leicht, rutschfest", color="schwarz", condition="sehr gut", type="accessory", score=7),
        Wardrobe(name="Sandalen (Weiß)", description="Leicht, bequem, sommerlich", color="weiß", condition="gut", type="shoes", score=7),
        Wardrobe(name="Sneaker Lite (Hellgrau)", description="Ultraleicht, atmungsaktiv", color="hellgrau", condition="gut", type="shoes", score=7),

        # ALLE JAHRESZEITEN / LAYERING (All seasons)
        Wardrobe(name="Übergangsjacke (Oliv)", description="Leicht gefüttert, für Frühling/Herbst", color="oliv", condition="gut", type="outerwear", score=8),
        Wardrobe(name="Trenchcoat (Beige)", description="Wettertauglich, klassisch, Übergang", color="beige", condition="sehr gut", type="outerwear", score=9),
        Wardrobe(name="Overshirt (Karo Blau/Rot)", description="Perfekt zum Layern, dickes Flanell", color="blau/rot", condition="gut", type="top", score=8),
        Wardrobe(name="Cardigan (Creme)", description="Layering, weich, Alltag", color="creme", condition="gut", type="top", score=7),
        Wardrobe(name="Basic Longsleeve (Hellblau)", description="Ganzjahres-Basic, Baumwolle", color="hellblau", condition="neu", type="top", score=7),
        Wardrobe(name="Jeans Straight Fit (Indigo)", description="Robust, ganzjährig tragbar", color="indigo", condition="gut", type="bottom", score=8),
        Wardrobe(name="Sneaker Allround (Weiß/Grün)", description="Alltag, bequem, passt zu allem", color="weiß/grün", condition="sehr gut", type="shoes", score=8),
        Wardrobe(name="Daypack (Schwarz/Orange)", description="Alltag, wetterresistent, 18L", color="schwarz/orange", condition="gut", type="bag", score=8),

        # EXTRA: MIXED WEATHER (wechselhaft)
        Wardrobe(name="Packbare Regenhülle Rucksack (Neonorange)", description="Wasserdichte Cover, reflektierend", color="neonorange", condition="neu", type="accessory", score=7),
        Wardrobe(name="Hybridjacke (Schwarz/Gelb)", description="Winddicht, leicht isoliert, wasserabweisend", color="schwarz/gelb", condition="sehr gut", type="outerwear", score=8),
        Wardrobe(name="Thermo-Beanie (Petrol)", description="Extra warm, feuchtigkeitsableitend", color="petrol", condition="neu", type="headwear", score=7),
        Wardrobe(name="Fleece-Leggings (Grau)", description="Warm, als Layer unter Hose", color="grau", condition="gut", type="bottom", score=7),
        Wardrobe(name="Wanderstiefel Waterproof (Schwarz)", description="Wasserdicht, stabil, griffig", color="schwarz", condition="sehr gut", type="shoes", score=9),
        Wardrobe(name="Merino-Socken Trail (Grün)", description="Polsterzonen, warm & trocken", color="grün", condition="neu", type="socks", score=8)
    )

    session.add_all(items)
    session.commit()

#create_item_weather_50()