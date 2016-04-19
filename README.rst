Bipartite graphs frequently emerge in situations where we aren't necessarily looking them -- for example, any two sequences of integers determines a bipartite graph.  Under more natural circumstances, database columns (particularly columns representing keys or partial keys) can sometimes be better understood in terms of bipartite relations.

This repo provides a simple algorithm that partitions a bipartite graph (given its edge sequences) into categories of forests that are stricly 1-1, 1-to-many, many-to-1, and many-to-many, and provides some basic tabulations for each category.

The initial application was in fact a small database project for which there were columns alleging to be primary or foreign keys, but weren't really (presumably due to quality control issues).  It was helpful to understand at least whether they keys were mostly unique, mostly many-to-1 or 1-to-many, etc, and then to look for pockets of outliers (which were presumbed to be misentered or wrongly loaded keys).
