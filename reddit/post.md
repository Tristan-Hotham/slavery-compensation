**Title:** [OC] When Britain ended colonial slavery it paid £20 million to the slave-owners, not the enslaved. Here are 3,187 British addresses of the owners and claimants: 36% were in London

**Body:**

In 1833 Parliament abolished slavery in most British colonies and voted £20 million (about 40% of government spending that year) to compensate the owners. The people who had been enslaved received nothing, and most were made to work unpaid as "apprentices" until 1838.

UCL's Legacies of British Slavery database has traced many of the owners and claimants to addresses in Britain. I mapped the 3,187 it has located in Great Britain (no names used) against the 1831 census:

- London: 1,158 addresses, 36%. Middlesex alone has 33% of the addresses and had 8% of the people.
- Then Edinburgh (121), Bristol (106), Liverpool (100) and Bath (66).
- Per head, Scotland (2.1 per 10,000) matches England (2.0); Wales is far lower (0.5).
- Addresses thin out with distance from the ports, about 37% fewer per head for each doubling, but that is mostly a pull towards London and it is not robust to leaving out the South-East.
- About 44% of the country houses outside the towns are listed buildings today.

The LBS team's own caveat: "This map is a search tool and a general guide. More work is needed to produce data for statistical analysis." Only located addresses are shown (about 61% of those in their county table).

Interactive map (each dot links to a record at UCL): https://maps.tristanhotham.com/slavery-compensation/

**Source comment:**

Data: Legacies of British Slavery database, Centre for the Study of the Legacies of British Slavery, UCL (map address data, retrieved 2026; counts only, no names); 1831 census county totals (1851 census Population Tables I); listed buildings from Historic England, HES and Cadw (OGL). Method: Poisson regression of county counts with 1831 population as the base, plan written before the analysis. Tools: Python (pandas, statsmodels, geopandas, matplotlib), MapLibre. Paper and code: https://github.com/Tristan-Hotham/slavery-compensation
