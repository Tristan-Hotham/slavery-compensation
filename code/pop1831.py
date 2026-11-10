"""1831 census populations of the historic counties of Great Britain.

Source: Census of Great Britain, 1851. Population Tables I, Vol. I: Table XXX (England and Wales, p. clxviii) and Table X
(Scotland, p. ccxii), which reprint the 1801 to 1851 county totals; transcribed by Ditto Books, "Census population 1801 to 1851"
(https://dittobooks.co.uk/extras/census/census-population-1801-1851, retrieved 2026). 1841 totals from the same tables are kept
to compare with the LBS map's own population column. Keys use the county names of the LBS map (lbs_populations.json).
Yorkshire is the sum of the East, North and West Ridings and the City of York.
"""
# name: (1831, 1841, nation)
POP = {
    "Bedfordshire": (95483, 107936, "England"), "Berkshire": (146234, 161759, "England"), "Buckinghamshire": (146977, 156439, "England"),
    "Cambridgeshire": (143955, 164459, "England"), "Cheshire": (334391, 395660, "England"), "Cornwall": (301306, 342159, "England"),
    "Cumberland": (169262, 178038, "England"), "Derbyshire": (237170, 272202, "England"), "Devon": (493908, 532959, "England"),
    "Dorset": (159385, 175054, "England"), "Durham": (239256, 307963, "England"), "Essex": (317507, 344979, "England"),
    "Gloucestershire": (387398, 431495, "England"), "Herefordshire": (110617, 113272, "England"), "Hertfordshire": (142844, 156660, "England"),
    "Huntingdonshire": (53192, 58549, "England"), "Kent": (479558, 549353, "England"), "Lancashire": (1336854, 1667054, "England"),
    "Leicestershire": (197003, 215867, "England"), "Lincolnshire": (317465, 362602, "England"), "Middlesex": (1358330, 1576636, "England"),
    "Monmouthshire": (98126, 134368, "Wales"), "Norfolk": (390054, 412664, "England"), "Northamptonshire": (179336, 199228, "England"),
    "Northumberland": (236959, 266020, "England"), "Nottinghamshire": (225327, 249910, "England"), "Oxfordshire": (153526, 163127, "England"),
    "Rutland": (19385, 21302, "England"), "Shropshire": (213518, 225820, "England"), "Somerset": (403795, 435599, "England"),
    "Hampshire": (313976, 354682, "England"), "Staffordshire": (409480, 509472, "England"), "Suffolk": (296317, 315073, "England"),
    "Surrey": (486434, 584036, "England"), "Sussex": (272644, 300075, "England"), "Warwickshire": (336645, 401703, "England"),
    "Westmorland": (55041, 56454, "England"), "Wiltshire": (237244, 256280, "England"), "Worcestershire": (222655, 248460, "England"),
    "Yorkshire": (168891 + 26260 + 192206 + 984609, 194936 + 28842 + 204701 + 1163580, "England"),
    # Wales (Monmouthshire above: the census tables print it with England; the LBS map and this study place it in Wales)
    "Anglesey": (48325, 50891, "Wales"), "Brecknockshire": (47763, 55603, "Wales"), "Cardiganshire": (64780, 68766, "Wales"),
    "Carmarthenshire": (100740, 106326, "Wales"), "Caernarfonshire": (66818, 81093, "Wales"), "Denbighshire": (82665, 88478, "Wales"),
    "Flintshire": (60244, 66919, "Wales"), "Glamorgan": (126612, 171188, "Wales"), "Merionethshire": (35315, 39332, "Wales"),
    "Montgomeryshire": (66844, 69607, "Wales"), "Pembrokeshire": (81425, 88044, "Wales"), "Radnorshire": (24743, 25458, "Wales"),
    # Scotland
    "Ayrshire": (145055, 164356, "Scotland"), "Berwickshire": (34048, 34438, "Scotland"), "Bute": (14151, 15740, "Scotland"),
    "Clackmannanshire": (14729, 19155, "Scotland"), "Dumfriesshire": (73770, 72830, "Scotland"), "Dunbartonshire": (33211, 44296, "Scotland"),
    "Midlothian (Edinburgh)": (219345, 225454, "Scotland"), "Fife": (128839, 140140, "Scotland"),
    "Haddingtonshire (East Lothian)": (36145, 35886, "Scotland"), "Kinross-shire": (9072, 8763, "Scotland"),
    "Kirkcudbrightshire": (40590, 41119, "Scotland"), "Lanarkshire": (316819, 426972, "Scotland"),
    "Linlithgowshire (West Lothian)": (23291, 26872, "Scotland"), "Peeblesshire": (10578, 10499, "Scotland"),
    "Renfrewshire": (133443, 155072, "Scotland"), "Roxburghshire": (43663, 46025, "Scotland"), "Selkirkshire": (6833, 7990, "Scotland"),
    "Stirlingshire": (72621, 82057, "Scotland"), "Wigtownshire": (36258, 39195, "Scotland"), "Argyll": (100973, 97371, "Scotland"),
    "Aberdeenshire": (177657, 192387, "Scotland"), "Banffshire": (48337, 49679, "Scotland"), "Caithness": (34529, 36343, "Scotland"),
    "Moray": (34498, 35012, "Scotland"), "Forfarshire": (139606, 170453, "Scotland"), "Inverness-shire": (94797, 97799, "Scotland"),
    "Kincardineshire": (31431, 33075, "Scotland"), "Nairnshire": (9354, 9217, "Scotland"), "Orkney and Shetland": (58239, 61065, "Scotland"),
    "Perthshire": (142166, 137457, "Scotland"), "Ross & Cromarty": (74820, 78685, "Scotland"), "Sutherland": (25518, 24782, "Scotland"),
}
TOTALS_1831 = {"England": 13090523, "Wales": 806274, "Scotland": 2364386}   # printed totals; England includes Monmouthshire
TOTALS_1841 = {"England": 14997427, "Wales": 911705, "Scotland": 2620184}


def check():
    for yi, tot in ((0, TOTALS_1831), (1, TOTALS_1841)):
        s = {"England": 0, "Wales": 0, "Scotland": 0}
        for k, v in POP.items():
            nat = "England" if k == "Monmouthshire" else v[2]          # the printed England total includes Monmouthshire
            s[nat] += v[yi]
        assert s == tot, (yi, s, tot)
    return True


if __name__ == "__main__":
    print(check(), len(POP))
