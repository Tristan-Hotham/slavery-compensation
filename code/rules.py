"""Rules fixed in the analysis plan: county name mapping, geocode precision, address form, country-house candidates and the
distinctive part of a house name. Every hand decision is here."""
import re

# LBS county spellings and modern names -> historic county (keys of pop1831.POP). None = decide from the point (nearest 1851
# parish for England and Wales; by hand below for Scotland).
COUNTY = {
    "Middlesed": "Middlesex", "Lancashire, Merseyside": "Lancashire", "North Yorkshire": "Yorkshire", "West Yorkshire": "Yorkshire",
    "Yorkshire E.R.": "Yorkshire", "Cumbria": None, "London": None, "Powys": None,
    "Breconshire": "Brecknockshire", "Pembrokershire": "Pembrokeshire",
    "Aberdeen": "Aberdeenshire", "Angus": "Forfarshire", "Argyllshire": "Argyll", "Buteshire": "Bute", "Dumbartonshire": "Dunbartonshire",
    "East Lothian": "Haddingtonshire (East Lothian)", "Falkirk": "Stirlingshire", "Invernesshire": "Inverness-shire",
    "Isle of Skye": "Inverness-shire", "Kircudbrightshire": "Kirkcudbrightshire", "Kirkudbrightshire": "Kirkcudbrightshire",
    "Midlothian": "Midlothian (Edinburgh)", "Orkney": "Orkney and Shetland", "Peebles-shire": "Peeblesshire", "Roxburgh": "Roxburghshire",
    "Roxburgh-shire": "Roxburghshire", "Ross-shire": "Ross & Cromarty", "West Lothian": "Linlithgowshire (West Lothian)",
    "Galloway": None,
}
# Scottish rows without a usable county, decided by hand from the place named
SCOT_BY_PLACE = {"Isle of Lewis": "Ross & Cromarty", "Kirkmaiden": "Wigtownshire"}
# Galloway: the Cree divides Wigtownshire (west) from the Stewartry of Kirkcudbright (east)
CREE_LON = -4.42

PREC = {"building": "exact", "amenity": "exact", "leisure": "exact", "tourism": "exact", "historic": "exact", "office": "exact",
        "shop": "exact", "man_made": "exact", "railway": "exact", "highway": "street", "place": "area", "boundary": "area",
        "landuse": "area", "natural": "area"}

STREET_WORDS = r"street|st\.?|square|sq\.?|place|terrace|crescent|row|road|rd\.?|lane|buildings|parade|circus|gardens|walk|gate|wharf|quay|yard|inn|chambers|mews|alley|passage|hill|green|court|cottages|villas|esplanade|strand|steyne|grove|rise|vale|close|bridge|market|churchyard|wynd|close|port|parade"
STREET_RE = re.compile(r"\b(" + STREET_WORDS + r")\b", re.I)
NUM_RE = re.compile(r"^\s*(no\.?\s*)?\d+[a-z]?\b|,\s*\d+\s|\b\d+\s*(&|and|-)\s*\d+\b", re.I)
HOUSE_WORDS = ["hall", "house", "park", "court", "castle", "abbey", "manor", "grange", "priory", "place", "lodge", "towers", "tower",
               "mount", "hill", "wood", "villa", "cottage", "mansion", "palace", "seat", "farm", "estate", "bank", "lea", "field",
               "hurst", "combe", "ville", "grove", "mains", "mill"]
GENERIC = set(HOUSE_WORDS) | {"the", "of", "near", "old", "new", "great", "little", "upper", "lower", "north", "south", "east", "west",
                              "and", "at", "in", "on", "house", "st", "saint", "now", "later", "formerly", "or", "called"}
# words that mark a named property even when a street word appears (e.g. "Hampton Court" is a house, "Copthall Court" a street)
PROP_WORDS = re.compile(r"\b(hall|house|park|castle|abbey|manor|grange|priory|lodge|towers|villa|cottage|mansion|palace)\b", re.I)


def precision(cls):
    return PREC.get(cls, "area") if isinstance(cls, str) else "area"


INSTITUTION = re.compile(r"\b(asylum|hospital|college|school|academy|workhouse|prison|gaol|barracks|cathedral|infirmary|dockyard|citadel|retreat)\b", re.I)
END_STREET = re.compile(r"\b(street|square|terrace|crescent|row|road|lane|buildings|parade|circus|gardens|walk|wharf|quay|yard|mews|alley|passage|esplanade|strand|wynd|place)\s*$", re.I)


def address_form(street, cls):
    """street address / named house / institution / settlement only, from the street text and the OSM class (rules in NOTES.md)"""
    s = street.strip() if isinstance(street, str) else ""
    if not s:
        return "settlement only"
    head = re.split(r"[,(\[]", s)[0].strip()
    if NUM_RE.search(s):
        return "street address"
    if END_STREET.search(head):
        return "street address"
    if INSTITUTION.search(s):
        return "institution"
    if END_STREET.search(head):
        return "street address"
    if PROP_WORDS.search(head):
        return "named house"
    if STREET_RE.search(head):
        return "street address"
    if cls == "highway":
        return "street address"
    return "named house"


def distinctive(name):
    """the distinctive words of a house name, lower case, generic words removed; first part before a comma or bracket"""
    if not isinstance(name, str):
        return []
    n = re.split(r"[,(\[]| near | now | or ", name.lower())[0]
    n = re.sub(r"[^a-z' ]", " ", n).replace("'", "")
    return [w for w in n.split() if w not in GENERIC and len(w) > 2]


# listed great houses (England and Wales, Grade I and II*), rules from NOTES.md
GREAT_YES = re.compile(r"\b(hall|house|park|court|castle|abbey|manor|grange|priory|place)\b", re.I)
GREAT_NO = re.compile(r"\b(farm|farmhouse|cottage|cottages|barn|lodge|stable|stables|gate|gates|gateway|wall|walls|almshouse|almshouses|school|vicarage|rectory|parsonage|dovecote|granary|outbuilding|outbuildings|coach|bridge|church|chapel|summerhouse|garden|gazebo|temple|ice)\b", re.I)


def great_house(name, grade, typ):
    return (typ == "house") and (grade in ("I", "II*")) and bool(GREAT_YES.search(name or "")) and not GREAT_NO.search(name or "")


# listed-name side of the match: current-use words that do not change which building it is
USE_WORDS = {"school", "hotel", "college", "offices", "office", "council", "district", "club", "nursing", "home", "centre", "museum",
             "including", "attached", "with", "adjoining", "ruins", "remains", "former", "formerly", "now", "known", "as"}
ANCILLARY = re.compile(r"\b(lodge|lodges|cottage|cottages|farm|farmhouse|stable|stables|coach|carriage|gate|gates|gateway|pier|piers|wall|walls|"
                       r"barn|garage|garages|dovecote|church|chapel|road|street|terrace|lane|arms|inn|bridge|mill|kennels|lodging|"
                       r"temple|summerhouse|grotto|orangery|icehouse|obelisk|monument|mausoleum|tomb|well|bothy|steading|granary|outbuildings?)\b", re.I)
TYPE_WORDS = ["hall", "house", "park", "court", "castle", "abbey", "manor", "grange", "priory", "place", "towers", "tower", "mount",
              "lodge", "villa", "cottage", "mansion", "palace", "grove", "bank", "wood", "hill"]


def type_word(name):
    n = (name or "").lower()
    ws = re.findall(r"[a-z]+", n)
    for w in reversed(ws):
        if w in TYPE_WORDS:
            return w
    return None


def listed_key(name):
    n = re.sub(r"[^a-z' ]", " ", (name or "").lower()).replace("'", "")
    return [w for w in n.split() if w not in GENERIC and w not in USE_WORDS and len(w) > 2]


def same_house(cand_name, listed_name):
    """the hand-checked rule: same distinctive words, no ancillary building, compatible house type"""
    from rapidfuzz import fuzz
    a = distinctive(cand_name)
    if not a:
        return 0
    full = listed_name or ""
    head = re.split(r",|\(| and | with | including | attached ", full, flags=re.I)[0]
    best = 0
    for var in {full, head}:
        b = listed_key(var)
        if not b or a[0] not in b:
            continue
        sc = fuzz.ratio(" ".join(a), " ".join(b))
        if sc < 90:
            continue
        anc_l = set(m.lower() for m in ANCILLARY.findall(var))
        anc_c = set(m.lower() for m in ANCILLARY.findall(cand_name or ""))
        if anc_l - anc_c:
            continue
        tc, tl = type_word(cand_name), type_word(var)
        if tc and tl and tc != tl and not (tc == "park" and tl in ("house", "hall")):
            continue
        best = max(best, sc)
    return best
