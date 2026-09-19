'''
Curated category bank for puzzle generation. Each CategoryDefinition has a name,
exactly four unique words, and a difficulty color among: yellow, green, blue, purple.
Words are unique across the entire bank to ensure a unique solution when mixing categories.
'''
from dataclasses import dataclass
from typing import List
@dataclass(frozen=True)
class CategoryDefinition:
    name: str
    words: List[str]
    difficulty: str  # one of: yellow, green, blue, purple
def get_category_bank() -> List[CategoryDefinition]:
    # Note: All words are lowercase, single-token where possible, and unique across categories
    bank: List[CategoryDefinition] = [
        # Yellow (easiest)
        CategoryDefinition("Fruit", ["apple", "banana", "orange", "grape"], "yellow"),
        CategoryDefinition("Cardinal Numbers (1–4)", ["one", "two", "three", "four"], "yellow"),
        CategoryDefinition("Basic Units of Time", ["second", "minute", "hour", "day"], "yellow"),
        CategoryDefinition("Winter Clothing", ["coat", "scarf", "gloves", "boots"], "yellow"),
        CategoryDefinition("Sports Equipment", ["ball", "bat", "racket", "helmet"], "yellow"),
        CategoryDefinition("3D Shapes", ["cube", "sphere", "cone", "cylinder"], "yellow"),
        CategoryDefinition("Baked Goods", ["bread", "muffin", "bagel", "donut"], "yellow"),
        CategoryDefinition("Tools", ["hammer", "wrench", "pliers", "screwdriver"], "yellow"),
        CategoryDefinition("Kitchen Appliances", ["toaster", "blender", "microwave", "oven"], "yellow"),
        CategoryDefinition("Vehicles", ["car", "truck", "bicycle", "motorcycle"], "yellow"),
        CategoryDefinition("Computer Parts", ["keyboard", "mouse", "monitor", "cpu"], "yellow"),
        CategoryDefinition("Movie Genres", ["comedy", "drama", "horror", "thriller"], "yellow"),
        CategoryDefinition("Weather Events", ["rain", "snow", "thunder", "hail"], "yellow"),
        # Green (medium)
        CategoryDefinition("Planets", ["mercury", "venus", "earth", "mars"], "green"),
        CategoryDefinition("Quadrilaterals", ["square", "rectangle", "rhombus", "trapezoid"], "green"),
        CategoryDefinition("Programming Languages", ["python", "java", "swift", "rust"], "green"),
        CategoryDefinition("Web Protocols", ["http", "https", "ftp", "smtp"], "green"),
        CategoryDefinition("Dog Breeds", ["beagle", "poodle", "bulldog", "labrador"], "green"),
        CategoryDefinition("Musical Instruments", ["violin", "piano", "trumpet", "flute"], "green"),
        CategoryDefinition("Trees", ["oak", "pine", "maple", "birch"], "green"),
        CategoryDefinition("Birds", ["eagle", "sparrow", "robin", "pigeon"], "green"),
        CategoryDefinition("Sea Creatures", ["shark", "dolphin", "octopus", "squid"], "green"),
        CategoryDefinition("Board Games", ["chess", "checkers", "monopoly", "scrabble"], "green"),
        CategoryDefinition("Card Games", ["poker", "bridge", "hearts", "spades"], "green"),
        CategoryDefinition("File Image Extensions", ["jpg", "png", "gif", "bmp"], "green"),
        CategoryDefinition("Countries", ["china", "india", "brazil", "canada"], "green"),
        CategoryDefinition("U.S. States", ["texas", "florida", "ohio", "alaska"], "green"),
        CategoryDefinition("Tea Types", ["black", "green", "oolong", "white"], "green"),
        CategoryDefinition("Currency Units", ["dollar", "euro", "yen", "pound"], "green"),
        CategoryDefinition("Occupations", ["doctor", "teacher", "lawyer", "engineer"], "green"),
        CategoryDefinition("Zodiac Signs (set 1)", ["aries", "cancer", "libra", "virgo"], "green"),
        CategoryDefinition("Human Languages", ["english", "spanish", "french", "german"], "green"),
        CategoryDefinition("Root Vegetables", ["carrot", "beet", "radish", "turnip"], "green"),
        # Blue (harder)
        CategoryDefinition("Noble Gases", ["helium", "neon", "argon", "krypton"], "blue"),
        CategoryDefinition("Metric Prefixes (small)", ["milli", "micro", "nano", "pico"], "blue"),
        CategoryDefinition("Body Organs", ["heart", "liver", "kidney", "lungs"], "blue"),
        CategoryDefinition("Bones", ["femur", "tibia", "ulna", "radius"], "blue"),
        CategoryDefinition("Math Terms", ["integral", "vector", "matrix", "scalar"], "blue"),
        CategoryDefinition("Cloud Types", ["cirrus", "cumulus", "stratus", "nimbus"], "blue"),
        CategoryDefinition("Constellations", ["orion", "leo", "taurus", "gemini"], "blue"),
        CategoryDefinition("Capital Cities", ["paris", "tokyo", "london", "cairo"], "blue"),
        CategoryDefinition("Rivers", ["nile", "amazon", "danube", "thames"], "blue"),
        CategoryDefinition("Awards (Entertainment)", ["oscar", "emmy", "tony", "grammy"], "blue"),
        CategoryDefinition("Programming Paradigms", ["object", "functional", "procedural", "declarative"], "blue"),
        CategoryDefinition("Spacecraft / Missions", ["apollo", "voyager", "soyuz", "hubble"], "blue"),
        CategoryDefinition("Precious Stones", ["diamond", "emerald", "sapphire", "topaz"], "blue"),
        # Purple (trickiest)
        CategoryDefinition("Chess Pieces", ["king", "queen", "rook", "bishop"], "purple"),
        CategoryDefinition("Directions", ["north", "south", "east", "west"], "purple"),
        CategoryDefinition("Seasons", ["spring", "summer", "autumn", "winter"], "purple"),
        CategoryDefinition("Fast Synonyms", ["rapid", "quick", "brisk", "speedy"], "purple"),
        CategoryDefinition("Operating Systems", ["windows", "linux", "android", "ios"], "purple"),
        CategoryDefinition("Coffee Drinks", ["espresso", "latte", "cappuccino", "mocha"], "purple"),
        CategoryDefinition("Greek Letters", ["alpha", "beta", "gamma", "delta"], "purple"),
    ]
    # Sanity check for uniqueness across the entire bank
    seen = set()
    for cat in bank:
        for w in cat.words:
            lw = w.strip().lower()
            if lw in seen:
                raise ValueError(f"Duplicate word across category bank: {lw}")
            seen.add(lw)
    return bank