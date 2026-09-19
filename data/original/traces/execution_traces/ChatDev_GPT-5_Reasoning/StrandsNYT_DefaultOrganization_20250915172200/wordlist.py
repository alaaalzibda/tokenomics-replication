'''
A modest English word list (lowercase) used to validate "non-theme" words that
reward hints in the Strands puzzle. Words must be length >= 4 to count.
This is not exhaustive; you can expand as needed.
'''
WORDS = {
    # Common short words (4-7 letters)
    "soft", "ware", "wars", "sore", "rose", "rows", "soar", "toes", "tore", "tone",
    "twin", "twine", "tire", "wore", "wont", "went", "west", "wise", "wine",
    "ring", "wing", "wins", "wets", "swan", "sift", "swift", "snow", "sofa",
    "star", "start", "stare", "stew", "stow", "straw", "straws", "strawed",
    "stone", "store", "storm", "stomp", "snore", "snort",
    "snarl", "snows", "snout", "swing", "swore", "sworn",
    "python", "rust", "ruby", "kotlin", "scala", "swift", "julia", "goat",
    "coal", "cola", "goal", "goals", "golf", "gore", "gone",
    "tango", "tangoes", "tangoed", "tang", "tangy", "tilt", "tilts", "tins",
    "into", "pith", "thin", "thing", "things", "thaw", "thaws",
    "thinly", "thorn", "thorns",
    "sort", "sorts", "salt", "sail", "sails", "salsa", "silo", "silos", "siloed",
    "alto", "altar", "alter", "alert", "alerts", "alerted",
    "iron", "irons", "irony", "ions", "loin", "loins", "loan", "loans", "luna",
    "lunar", "lure", "lures", "lured", "lute", "lutes",
    "java", "perl", "lisp", "pascal",
    # Add some more common words
    "tone", "tones", "tunes", "tune", "tuned", "tuner",
    "tang", "tangs", "torn", "tore",
    "ore", "ores", "earn", "earns", "earned", "earl", "earls",
    "farm", "farms", "farmer", "farmers", "frame", "frames", "framed",
    "form", "forms", "formed", "former", "forage", "forages", "forge", "forged",
    "range", "ranges", "rang", "rangy", "rangier", "anger", "angers", "angry",
    "lion", "lions", "lioness", "loaner", "loaners", "solar", "soar",
    "soars", "soared", "softer", "soften", "softened", "softener",
    "wear", "wears", "wean", "weans", "weaned", "warn", "warns", "warned",
    "earnest", "near", "nears", "nearer", "nearest", "ear", "ears",
    # Some longer random additions
    "software", "warfare", "angle", "angles", "angler", "anglers",
    "orange", "oranges", "strange", "stranger", "strangers",
    # Just to increase diversity
    "frost", "frosts", "frosted", "stones", "stoneware",
    "snare", "snares", "snared", "sinew", "sinews", "waste", "waster", "wasted",
    "wastes",
}