"""The hand check of the listed-building match (NOTES.md). The rule in rules.same_house was developed on two earlier samples
(seeds 11/12 and 101/102), then frozen; this is the evaluation on fresh samples drawn with seeds 201 (matches) and 202
(non-matches) from SCR/candidates.parquet. I read each pair of names (and, for non-matches, the listed names within the search
radius that contain the first distinctive word) and judged it by eye.

MATCH_WRONG: positions (0 to 49) in the match sample where the listed entry is not, or not clearly, the candidate house
  (0 Mythe Villa to The Mythe; 8 Hallow Park to Hallow School; 9 Mythe House to The Mythe; 11 Ashe Park to Ashe House, a different
  house; 22 a parsonage 3.8 km away; 25 Kempock to a numbered street; 45 Tatton Park to Tatton Old Hall, not the mansion).
MISSED: positions in the non-match sample where the candidate house is clearly listed under a nearby entry the rule rejected
  (16 Harmony Hall, listed as Harmony House, Melrose; 35 Charborough House, listed as Charborough Park).
"""
SEED_MATCH, SEED_MISS, N = 201, 202, 50
# The evaluation samples as drawn (LBS map address_id, in sample order). They were drawn before two misplaced geocodes and two
# Guernsey rows were corrected in step 1 (reviewer fix, logged in NOTES.md); none of those rows is in either sample, so the samples
# are fixed here by id rather than redrawn, and the verdicts below still refer to the same houses.
MATCH_IDS = [2118254623, 2118254867, 2118251833, 1238245487, 2118254933, -1091375292, 2118258373, 2118256197, 2118257469, 2118254625, 1845183903, 2118254619, 2118253036, 2118254571, 2118254951, 2118250693, 1837535960, 274623378, 2118259077, 2118254727, 2118254719, 2118250637, 2118255719, 2118252953, 2118256585, 2118257503, 2118256911, 2118254467, 78, 2118254519, 405, 2118254317, 2118251525, 265, 2118250551, 904, 57, 2118253315, 900, 2118254687, 118, 2118250893, 221, 2118251539, 2118256723, 55, 1697711542, 2118251105, 2118252405, 2118253417]
NONMATCH_IDS = [68, 2118258725, 713322972, 2118251711, 2118255127, 2118251701, 2118256147, 2118251507, 280, 67, 2118253699, 461, 2118255089, 1335517439, 2118254073, 978, 2118253563, 2118254617, 2118258447, 2118251861, 2118253339, 2118256001, 442795852, 2118253521, 2118255927, 2118256377, 2118258903, 784, 2105220367, 2118254283, 414639966, 367, 862439463, 212, 1413287155, 193699078, 198, 765, 2118251545, 2118254285, 2118251919, 2118255845, 2118258861, 2118253781, 2118257481, -415985403, 2118254743, 2118254333, 463, -85852695]
MATCH_WRONG = [0, 8, 9, 11, 22, 25, 45]
MISSED = [16, 35]
