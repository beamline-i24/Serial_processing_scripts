# python packages
import pandas as pd

# find multiplicity from space-group table
def M(spacegroup):
    space_group_table = pd.read_csv( "tables/space_group_table.csv")
    M = space_group_table[space_group_table.space_group == spacegroup ][ "M" ].as_matrix()[0]
    return M

# find lattice from space-group table
def lattice(spacegroup):
    space_group_table = pd.read_csv( "tables/space_group_table.csv")
    lattice = space_group_table[space_group_table.space_group == spacegroup ][ "lattice" ].as_matrix()[0]
    return lattice

def m( spacegroup ):
    space_group_table = pd.read_csv( "tables/space_group_table.csv")
    m = space_group_table[space_group_table.space_group == spacegroup ][ "m" ].as_matrix()[0]
    return m
