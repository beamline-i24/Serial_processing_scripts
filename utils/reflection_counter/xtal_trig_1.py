# - requires math import
import numpy as np

# - define volume functions
def V_unit( a, b, c, alpha, beta, gamma ):
    cos_alpha = np.cos(alpha * (np.pi / 180))
    cos_beta = np.cos(beta * (np.pi / 180))
    cos_gamma = np.cos(gamma * (np.pi / 180))
    m_matrix = np.array([[a * a            , a * b * cos_gamma, a * c * cos_beta ], \
                         [a * b * cos_gamma, b * b            , b * c * cos_alpha], \
                         [a * c * cos_beta , b * c * cos_alpha, c * c            ]])
    m_matrix_det = np.linalg.det(m_matrix)
    V_unit = np.sqrt(m_matrix_det)
    return V_unit
 
def operators( a, b, c, alpha, beta, gamma, operator ):
    V = V_unit( a, b, c, alpha, beta, gamma )
    if operator == "a*" :
        return ( b * c * np.sin( np.radians( alpha ) ) ) / V
    if operator == "b*" :
        return ( a * c * np.sin( np.radians( beta ) ) ) / V
    if operator == "c*":
        return ( a * b * np.sin( np.radians( gamma ) ) ) / V