# - requires math import
import math

# - define volume functions
def cubic( a, b, c, alpha, beta, gamma ):
    try:
        if a != b or a != c or b != c:
            raise ValueError, "lattice length error! in a cubic lattice a == b == c"
        if a < 0 or b < 0 or c < 0:
            raise ValueError, "lattice length error! a, b, c > 0"
        if alpha != 90 or beta != 90 or gamma != 90:
            raise ValueError, "lattice angle error! in a cubic lattice alpha, beta, gamma == 90"
        else:
            return True
    except ValueError, value:
        print value

def tetragonal( a, b, c, alpha, beta, gamma):
    try:
        if a != b:
            raise ValueError, "lattice length error! in a tetragonal lattice a == b"
        if c == a or c == b:
            raise ValueError, "lattice length error! c != b or a"
        if a < 0 or b < 0 or c < 0:
            raise ValueError, "lattice length error! a, b, c > 0"
        if alpha != 90 or beta != 90 or gamma != 90:
            raise ValueError, "lattice angle error! in a tetragonal lattice alpha, beta, gamma == 90"
        return True
    except ValueError, value:
        print value

def hexagonal( a, b, c, alpha, beta, gamma):
    try:
        if a != b:
            raise ValueError, "lattice length error! in a hexagonal lattice a == b"
        if a < 0 or b < 0 or c < 0:
            raise ValueError, "lattice length error! a, b, c > 0"
        if alpha != 90 or beta != 90 or gamma != 120:
            raise ValueError, "lattice angle error! in a hexagonal lattice alpha, beta == 90, gamma == 120 "
        return True
    except ValueError, value:
        print value

def trigonal( a, b, c, alpha, beta, gamma):
    try:
        if a != b:
            raise ValueError, "lattice length error! in a trigonal lattice a == b"
        if a < 0 or b < 0 or c < 0:
            raise ValueError, "lattice length error! a, b, c > 0"
        if alpha != 90 or beta != 90 or gamma != 120:
            raise ValueError, "lattice angle error! in a trigonal lattice alpha, beta == 90, gamma == 120 "
        return True
    except ValueError, value:
        print value

def orthorhombic( a, b, c, alpha, beta, gamma):
    try:
        if a == b or a == c or b == c:
            raise ValueError, "lattice length error! in an orthorhombic lattice a != b != c"
        if alpha != 90 or beta != 90 or gamma != 90:
            raise ValueError, "lattice angle error! in an orthorhombic lattice alpha, beta, gamma == 90 "
        return True
    except ValueError, value:
        print value

def monoclinic( a, b, c, alpha, beta, gamma):
    try:
        if a == b or a == c or b == c:
            raise ValueError, "lattice length error! in an monoclinic lattice a != b != c"
        if a < 0 or b < 0 or c < 0:
            raise ValueError, "lattice length error! a, b, c > 0"
        if alpha != 90 or gamma != 90 or beta == 90:
            raise ValueError, "lattice angle error! in an monoclinic lattice alpha, gamma == 90, beta != 90"
        if beta > 180 or beta < 0 :
            raise ValueError, "lattice angle error! 0 < beta < 180 and not 90"
        return True
    except ValueError, value:
        print value

def triclinic( a, b, c, alpha, beta, gamma):
    try:
        if a == b or a == c or b == c:
            raise ValueError, "lattice length error! in an triclinic lattice a != b != c"
        if a < 0 or b < 0 or c < 0:
            raise ValueError, "lattice length error! a, b, c > 0"
        if alpha == 90 or beta == 90 or gamma == 90:
            raise ValueError, "lattice angle error! in an monoclinic lattice alpha, beta, gamma != 90 "
        if alpha < 0 or alpha > 180 or beta > 180 or beta < 0 or gamma < 0 or gamma > 180:
            raise ValueError, "lattice angle error! 0 < alpha, beta, gamma < 180 and not 90"
        if ( 1 - ( math.cos ( math.radians ( alpha ) ) )**2 - ( math.cos ( math.radians ( beta ) ) )**2 - ( math.cos ( math.radians ( gamma ) ) )**2 + 2 * math.cos ( math.radians ( alpha ) ) * math.cos ( math.radians ( beta ) ) * math.cos ( math.radians ( gamma ) ) ) < 0:
            raise ValueError, "lattice angle error! this combination of cell angles do not give rise to a closed cell"
        return True
    except ValueError, value:
        print value
