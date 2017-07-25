What's in here?
---------------

This repo provides a simple Python class (``ezbpg.BipartiteGraph``) for representing simple (unweighted) Bipartite Graphs, and for answering a few basic questions about their properties.  It doesn't handle other kinds of graphs, it doesn't scale to petabytes or tie directly to a graph database, and it doesn't do any fancy algorithms.  The focus is on simplicity (it has no dependencies outside of the standard library) and ease of use while aiming to stay reasonably performant. 

Sample usage might go like this:

.. code:: python

    import ezbpg
    from tabulate import tabulate

    g = ezbpg.slurp(filepath)    # slurp a Graph from a CSV
    p = g.partition()            # obtain a structured partition
    rows,total = p.describe()


More Background
---------------

Bipartite graphs frequently emerge in situations where we aren't necessarily looking them -- for example, any pair of integer sequences (of the same length) determines a bipartite graph.  Under more natural circumstances, database columns (particularly columns representing keys or partial keys) can sometimes be better understood in terms of bipartite relations.  

This repo provides a few simple algorithms for generating basic summary statistics on bipartite graphs, so as to help determine their basic character, or "shape."  The first of these partitions a bipartite graph (given its edge sequences) into categories of forests that are stricly 1-1, 1-to-many, many-to-1, and many-to-many, and provides some basic tabulations for each category.  Other summary functions are in the works (for example, to help identify densely connected components within larger but more sparsely connected graphs). 

The initial application was in fact a small database project for which there were columns alleging to be primary or foreign keys, but weren't really (presumably due to quality control issues).  It was helpful to understand at least whether they keys were mostly unique, mostly many-to-1 or 1-to-many, etc, and then to look for pockets of outliers (which were presumbed to be misentered or wrongly loaded keys).

Why not use networkx?
---------------------

There is of course that fine, strongly vetted and widely used general-purpose graph modeling package, networkx.  If you're working on a larger analysis project and want to use something standardized and, perhaps more importantly, generalizable, then by all means, use networkx. 

However, the basic container for bipartite graph is so simple that I chose to implement it natively rather than require networkx as an external dependency.  There are also certain aspects of the networkx interface that don't quite "mesh" with the algorithms I'm working on (for performance and other considerations which I'll describe later); so for the time being the native interface feels more fungible. 

Status
------

The core algorithm seems to be quite solid; it just needs packaging (and perhaps a proper test suite). 
