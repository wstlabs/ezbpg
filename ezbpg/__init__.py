"""Provides a container class for simple BipartiteGraphs, with summary statistics.

Sample usage goes like this:

    import ezbpg

    g = ezbpg.read_csv(args.infile)
    r = g.partition().refine()
    r.describe()
"""
__version__ = '0.1.3'

from .core import BipartiteGraph, RefinedPartition
from typing import Dict, Any, Optional

def read_csv(path: str, encoding: str = 'utf-8', csvargs: Optional[Dict[str, Any]] = None) -> BipartiteGraph:
    return BipartiteGraph.read_csv(path, encoding, csvargs)

