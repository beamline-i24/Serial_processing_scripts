# modules
import re

# get spacegroup
def spacegroup(header):
    try:
        pattern = re.search( r"REMARK\s\d+\sSYMMETRY\sOPERATORS\sFOR\sSPACE\sGROUP:\s(\D\s\d+\s\d+\s\d+)", header )
        doi = pattern.group(1)
        if AttributeError:
            return doi
    except AttributeError:
        return "the spacegroup does not seems to be present in the pdb, is this actually a pdb file?"

# get cell a
def cell(header, cell):
    try:
        pattern = re.search( r"CRYST1\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\d+\.\d+)\s*(\D\s\d+\s\d+\s\d+)", header )
        a = float( pattern.group(1) )
        b = float( pattern.group(2) )
        c = float( pattern.group(3) )
        alpha = float( pattern.group(4) )
        beta = float( pattern.group(5) )
        gamma = float( pattern.group(6) )
        if AttributeError:
            if cell == "a":
                return a
            elif cell =="b":
                return b
            elif cell =="c":
                return c
            elif cell =="alpha":
                return alpha
            elif cell =="beta":
                return beta
            elif cell =="gamma":
                return gamma
    except AttributeError:
        return "a, b, c, alpha, beta, gamma does not seems to be present in the pdb, is this actually a pdb file?"

