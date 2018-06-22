#modules
import pandas as pd
import numpy as np
import math as m
import timeit
from cctbx import miller
from cctbx import crystal
import matplotlib.pyplot as plt
import pylab
import regex as re

#my modules
import xtal_trig_1 as trig
import unit_cell_check as check
import space_group as sp
import pdb_header_scrub as pdb

#functions
def get_parameters_pdb( header ):
    # open header file
    file = open( header )
    header = file.read()
    # extract unit cell data
    a = pdb.cell( header, "a" )
    b = pdb.cell( header, "b" )
    c = pdb.cell( header, "c" )
    alpha = pdb.cell( header, "alpha" )
    beta = pdb.cell( header, "beta" )
    gamma= pdb.cell( header, "gamma" )
    spacegroup = pdb.spacegroup( header )
    return spacegroup, a, b, c, alpha, beta, gamma
    file.close()

def gen_hkl( spacegroup, a, b, c, alpha, beta, gamma, d_min ):
    # generate hkls based on spacegroup, unit cell dimensions and d_min
    ms = miller.build_set(
                        crystal_symmetry=crystal.symmetry(
                                                        space_group_symbol = "P1",
                                                        unit_cell = ( a, b, c, alpha, beta, gamma ) ),
                        anomalous_flag = True,
                        d_min = d_min,
                        d_max = 50,
                        )
    hkl_list = list( ms.indices() )
    # put hkl_list in a pandas dataframe
    cols = [ "h", "k", "l" ]
    df = pd.DataFrame( hkl_list, columns=cols )
    return df

def scale_lattice( spacegroup, a, b, c, alpha, beta, gamma, lattice ):
    # scaler for spacegroup
    a_star = trig.operators( a, b, c, alpha, beta, gamma, "a*" )
    b_star = trig.operators( a, b, c, alpha, beta, gamma, "b*" )
    c_star = trig.operators( a, b, c, alpha, beta, gamma, "c*" )
    scaler = np.array( [ a_star, b_star, c_star ] )
    list_hkl = np.multiply( lattice, scaler )
    return list_hkl
    
def omega_d( h, k, l, wavelength, variable ):
    #import hkls as array
    hkl = np.array( [ h, k, l ] )
    # transpose array
    hkl = np.transpose( hkl )
    # calculate length of vector
    d_star = np.linalg.norm( hkl, axis=1 )
    # calculate ewald omega for vector of given length
    omega = np.degrees( np.arcsin( ( d_star * wavelength ) / 2 ) )
    if variable == "d_hkl":
        return 1 / d_star
    elif variable == "omega":
        return omega

def apply_d_omega( lattice, wavelength ):
    # hkl array
    df = lattice
    # calculate ewald omegas using omega function
    df[ "ewald_omega" ] = omega_d( df[ "h" ].values, df[ "k" ].values, df[ "l" ].values, wavelength, "omega" )
    return df
    
def det_vector_generator():
    # generate random varibles for circle
    phi = np.random.uniform( 0, 2*m.pi )
    cos_theta = np.random.uniform( -1, 1 )
    theta = m.acos( cos_theta )
    r = 1
    # generate x,y,z coordinates
    x = r * m.sin( theta) * m.cos( phi )
    y = r * m.sin( theta) * m.sin( phi )
    z = r * m.cos( theta )
    det = np.array( [ [ x, y, z ] ] )
    return det

def det_hkl_dot( det, h, k, l ):
    # (axb)/(a.b) = tan omega
    # import hkls as array
    hkl = np.array( [ h, k, l ] )
    # calculate dot product between det vector and hkl
    dot = np.dot( det, hkl )
    # transpose hkl to vectorise np.cross
    hkl = np.transpose( hkl )
    # cross product vector of det vector and hkl
    cross = np.cross( det, hkl )
    # mod of cross
    cross_mod = np.linalg.norm( cross, axis=1 )
    # transpose cross_mod to vectorise np.arctan2
    cross_mod = np.transpose( cross_mod )
    # anti_omega = angle between det vector and hkl
    anti_omega = np.arctan2( cross_mod, dot )
    # tranpose for vectorisation
    anti_omega = np.transpose( anti_omega )
    # omega = anit omega - 90
    omega = 90 - np.degrees( anti_omega )
    return abs( omega )

def spot_hist_plt( spot_df ):
    frequency = spot_df[ "spots" ].values
    plt.hist( frequency )
    plt.title( "frequency of bragg reflections per image" )
    plt.xlabel( "no. of bragg candidates per image" )
    plt.ylabel( "frequency" )
    pylab.show()

def hkl_plot( df_hkl ):
    df = pd.DataFrame()
    bins = 50
    bin_range, labels = pd.cut( df_hkl[ "d_star" ], bins=bins, retbins=True )
    df_hkl[ "bin" ] = pd.cut( df_hkl[ "d_star" ], bins=len( labels ), labels=labels )
    df[ "frequency" ] = df_hkl.groupby( "bin" )[ "frequency" ].mean()
    frequency = df[ "frequency" ].values
    d_hkl = df.index.values    
    plt.scatter( d_hkl, frequency )
    plt.title( "frequency of bragg reflections per image" )
    plt.xlabel( r'$\sin\theta/2\lambda$' )
    plt.ylabel( "frequency" )
    pylab.show()

def image_max( spacegroup, ano, variable ):
    m = sp.m( spacegroup )
    max = 562.5 / m
    if variable == "max":
        try:
            if ano == "True":
                return max
            elif ano == "False":
                return max / 2
            else:
                raise ValueError, "ano must be either True or False"
        except ValueError:
                print value
    elif variable == "scale":
        return 100 / max

def main( wavelength ):
    # collect spacegroup paremeters from pdb
    print "collecting unit cell parameters from pdb"
    spacegroup, a, b, c, alpha, beta, gamma = get_parameters_pdb( header )
    spacegroup = spacegroup.replace(" ", "")
    print "spacegroup = {0}".format( spacegroup )
    print "a, b, c, alpha, beta, gamma = {0}, {1}, {2}, {3}, {4}, {5}".format( a, b, c, alpha, beta, gamma )
    # define precision when calculating hkls on the ewald sphere 0 = no decimal place, 1 = 1 decimal place etc
    precision = 3
    mosaicity = 0.025
    # generate hkl lattice
    print "generating hkls"
    df_hkl = gen_hkl( spacegroup, a, b, c, alpha, beta, gamma, d_min )
    # scale hkls
    print "scale hkls" 
    df = scale_lattice( spacegroup, a, b, c, alpha, beta, gamma, df_hkl )
    # generate omegas
    print "calculating ewald omegas"
    df = apply_d_omega( df, wavelength )
    # variables for while loop
    df[ "frequency" ] = 0
    images = 0
    median = 0
    spot_no_2 = np.array( [ [ 0 ] ] )
    # defines max number of spots required
    max = image_max( spacegroup, ano, "max" )
    # returns output of hkl where the detector vector omega = ewald omega
    print "begin bragg reflection generation"
    while ( median < max ):
        # new detector vector
        det_vector = det_vector_generator()
        # creates a detector/hkl* omega column
        df[ "det_hkl_omega" ] = det_hkl_dot( det_vector, df[ "h" ].values, df[ "k" ].values, df[ "l" ].values )
        # compared ewald omega and detect omega - write +1 to frequency column
        df = df.round( { "ewald_omega" : precision, "det_hkl_omega" : precision } )
        # define emega width based on mosaicity
        ewald_low = df.ewald_omega - mosaicity
        ewald_high = df.ewald_omega + mosaicity
        # increase hkls hit by 1
        df[ "frequency_1" ] = np.where( ( ewald_low <= df.det_hkl_omega ) & ( df.det_hkl_omega <= ewald_high ), 1, 0 )
        df[ "frequency" ] = df[ "frequency" ] + df[ "frequency_1" ]
        # while loop house keeping
        images = images + 1
        median = df[ "frequency" ].median()
        median_scale = round( median * image_max( spacegroup, ano, "scale" ), 0 )
        spots = df[ "frequency_1" ].sum()
        print "image = {0}, median hkl frequency = {1}, spots on image = {2}".format( images, median_scale, spots )
        # concantenating data from spot outputs
        spot_no = np.array( [ [ spots ] ] )
        spot_no_2 = np.concatenate( ( spot_no_2, spot_no ), axis=0 )
        spot_df = pd.DataFrame( spot_no_2, columns=[ "spots" ] )
    # plot hist of spots
    spot_hist_plt( spot_df )
    spot_df.to_csv( "output/spot_hist.txt", sep="\t", mode="w" )
    print "finished"
    return images

wavelength = 0.9686
header = "/Users/slave/Documents/work/projects/pdb/pdb_headers/2FCQ.txt"
d_min = 1.5
ano = "False"

main(wavelength)
