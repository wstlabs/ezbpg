Sample data sets, for testing and otherwise.

Each is a CSV represent a list of vertex pairs for a simple bipartite graph. 

First, some small generic graphs:

* `null.csv` - an empty data set.
* `simple.csv` - a small sample data set that exercises some basic connectivity cases. 

The other files represent real-life datasets from the NYC real estate ecosystem, and are illustrative of the everyday weirdness involved in working with this data.

`declare.csv` - a moderately large (500k edges) list of condo declaration associations, taken from the ACRIS dataset:

* The first column a BBL (a unique property ID) 
* The second column is a unique identifier to a special filing document known as a *condominium declaration*  

The 'nychpd-' and 'dhcr-' datasets, meanwhile, represent associations been tax lots (that is, physical tract of land) and buildings, as denoted by BBL and BIN identifiers respectively.  In general we can expect these relations to be usually `1-to-1`, and sometimes `1-to-many` -- that is, if our data accurately reflect the real world.  

Unfortunately, in the data sets published by the city, there are frequently small numbers of rows with corrupted (or wrongly assigned) identifiers for the BBL, BIN or both, which can cause no end of headaches when attempting to analyze this data.  So this tool was written with precisely the goal in mind of sussing out these corrupted relations. 

