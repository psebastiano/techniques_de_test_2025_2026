"""Fichier de configuration de Pytest Défintion des fixtures."""
import http.client
import random
import struct
from typing import cast
from unittest.mock import Mock, patch

import pytest

from application.custom_types import PointSet_Geom, Triangles_Geom, Triangulation_Result


# Fixture - test_check_valid_uuid.py
@pytest.fixture(params=[
    "a1b2c3d4-e5f6-7890-1234-567890abcdef",  # Standard
    "00000000-0000-0000-0000-000000000000",  # Zéro
    "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF"   # Max
])
def uuid_str_valide(request):
    """Fournit des UUID valides en entrée pour tester le succès."""
    return request.param

@pytest.fixture(params=[
    " a1b2c3d4-e5f6-7890-1234-567890abcdef",  # Space at beginning
    "a1b2c3d4-e5f6-7890-1234-567890abcdef ",  # Space at end
    "not_a_uuid",  #Evident
    "FFFFFFFF-FFFF-FFFF-FFFF",
    12345,                                    # Integer
    None,                                     # NoneType
    True,                                     # Boolean
    b'some_bytes',                            # Bytes
    {'key': 'value'}                          # Dictionary   # Not long enough
])
def uuid_str_non_valide(request):
    """Fournit des UUID non valides en entrée pour tester l'échec."""
    return request.param



# Fixture - test_decode_binary_point_set_to_geometric.py
@pytest.fixture(params=[
    # --- cas 1 : Zéro point (N=0)----
    {
        "encoded_binary": struct.pack('I', 0), #I : unsigned long sur 4 octets
        "decoded_geometric": cast(PointSet_Geom, [])
    },
    # --- cas 2 : Un seul point (N=1)----
    # N =1, x = 5.5, y=12.3
    #I : unsigned long sur 4 octets
    #f : float sur 4 octets
    {
        "encoded_binary": struct.pack('Iff', 1, 5.5, 12.3),
        "decoded_geometric": cast(PointSet_Geom, 
            [{'x': 5.5, "y": 12.3}]
            )
    },
    # --- cas 3 : Deux points (N=2)----
    # N=1, x = 5.5, y=12.3
    # N=2, x = 1, y=13
    {
        "encoded_binary": struct.pack('Iffff', 2, 5.5, 12.3, 1.0, 13.0),
        "decoded_geometric": cast(PointSet_Geom, [
            {'x': 5.5, "y": 12.3}, 
            {'x': 1, "y": 13}
            ])
    }
])
def point_set_binary_geometric_pairs(request):
    """Fournit des paires binaires/géométrique pour les tests de décodage."""
    return request.param



# Fixture - test_encode_triangulation_result_to_binary.py
@pytest.fixture(params=[
    # --- cas 1 : Trois point, Un triangle (N=3, M=1), ---- #Les cas avec 
    # 0, 1 ou 2 points seront vérifiés dans la fonciont compute_triangulation
    {
        "geometric_input": cast(Triangulation_Result, {
            'points':[
                {'x': 0.0,'y': 0.0},
                {'x': 1.0,'y': 0.0},
                {'x': 0.0,'y': 1.0}
            ],
            'triangles':[
                {'v1': 0, 'v2': 1, 'v3': 2}
            ]
        }),
        "encoded_binary_expected":(
            struct.pack('I', 3) + 
            struct.pack('ffffff', 0.0, 0.0, 1.0, 0.0, 0.0, 1.0) + 
            struct.pack('I', 1) + 
            struct.pack('III', 0, 1, 2)
            
        )
    },
    # --- cas 2 : Quatre point, 2 Triangle (N=4, M=2)    
    {
        "geometric_input": cast(Triangulation_Result, {
            'points':[
                {'x': 0.0,'y': 0.0},
                {'x': 1.0,'y': 0.0},
                {'x': 0.0,'y': 1.0},
                {'x': 1.0,'y': 1.0}
            ],
            'triangles':[
                {'v1': 0, 'v2': 1, 'v3': 2},
                {'v1': 0, 'v2': 1, 'v3': 3},   
            ]
        }),
        "encoded_binary_expected":(
            struct.pack('I', 4) + 
            struct.pack('ffffffff', 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0) + 
            struct.pack('I', 2) + 
            struct.pack('IIIIII', 0, 1, 2, 0, 1, 3)
            
        )
    },
])
def triangulations_geometric_binary_pairs(request):
    """Fournit des paires binaires/géométrique pour les tests de d'encodage.
    
    Test d'encodage des valeurs retournés par le triangulateur : 
    Une liste de point + Les triangles obtenu par l'algorithme.
    """
    return request.param



# ------------ Test psm_client_fetch_data -------------# 
########################################################
# One helper function, to set up mock behaviour
# One parameterized fixture to go through all test cases

def setup_mock_response(status_code, body=b'', content_type='application/octet-stream'):
    """Create and configure a mock http.client.HTTPResponse object."""
    mock_response = Mock(spec=http.client.HTTPResponse)
    mock_response.status = status_code
    mock_response.read.return_value = body
    mock_response.getheaders.return_value = [('Content-Type', content_type)]
    return mock_response

#Response bodies named here to ease readability
MOCK_POINT_SET_DATA = b'\x10\x20\x30\x40\x50\x60' #Simulate a correct response body
MOCK_ERROR_400 = b'{"error": "Bad Request: Invalid UUID"}' #Error 400 response body
MOCK_ERROR_404 = b'{"error": "Not Found"}' #Error 404 response body
MOCK_ERROR_503 = b'{"error": "Service Unavailable"}' #Eerror 503 response body

@pytest.fixture(params=[
    #Case ID: (Status, Body, Expected Exception, Content Type)
    ("success_200", 200, MOCK_POINT_SET_DATA, 'application/octet-stream'),
    ("bad_request_400", 400, MOCK_ERROR_400, 'application/json'),
    ("not_found_404", 404, MOCK_ERROR_404, 'application/json'),
    ("unavailable_503",  503,  MOCK_ERROR_503, 'application/json')
])
def mock_psm_connection(request):
    """Parameterized fixture that mocks http.client.HTTPConnection."""
    #Unpack the parameters
    case_id, status_code, body, content_type = request.param

    with patch('http.client.HTTPConnection') as mock_connection_class:
        mock_instance = mock_connection_class.return_value

        mock_response = setup_mock_response(status_code, body, content_type)
        mock_instance.getresponse.return_value = mock_response
        
        # Attach configuration for the test function to assert against
        mock_instance.status_code = status_code
        mock_instance.body = body

        yield mock_instance


########################################################
########################################################


# -----------Test triangulation_compute ---------------#
########################################################

# Case 1 - Minimal required input (3 non colinear points -> 1 Triangle)
INPUT_1_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': 0.0, 'y': 0.0}, #Index 0
    {'x': 10.0, 'y': 0.0}, #Index 1
    {'x': 5.0, 'y': 10.0}, #Index 2
])
OUTPUT_1_triangles = Triangles_Geom = cast(Triangles_Geom, [
    {'v1': 0, 'v2': 1, 'v3': 2}
])
OUTPUT_1_Triangulation_Result = {
    'points' : INPUT_1_pointSet,
    'triangles' : OUTPUT_1_triangles
}
MESSAGE_1 = "Succes."

# Case 2 - A square (4 points, 2 triangles)
INPUT_2_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': 0.0, 'y': 0.0}, #Index 0
    {'x': 10.0, 'y': 0.0}, #Index 1
    {'x': 10.0, 'y': 10.0}, #Index 2
    {'x': 0.0, 'y': 10.0}, #Index 3
])
# Note: The test function already handles the two valid output possibilities by normalizing the triangles.
OUTPUT_2_triangles = cast(Triangles_Geom, [ 
    {'v1': 0, 'v2': 1, 'v3': 3},
    {'v1': 1, 'v2': 2, 'v3': 3}
])
OUTPUT_2_Triangulation_Result = {
    'points' : INPUT_2_pointSet,
    'triangles' : OUTPUT_2_triangles
}
MESSAGE_2 = "Succes."

# Case 3 - Empty Input - Should raise an error
INPUT_3_pointSet: PointSet_Geom = cast(PointSet_Geom, [])
OUTPUT_3_triangles = None
OUTPUT_3_Triangulation_Result = None
MESSAGE_3 = "Le PointSet est vide"

# Case 4 - Too few points - Should raise an error
INPUT_4_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': 1.0, 'y': 1.0}, #Index 0
    {'x': 2.0, 'y': 2.0} #Index 1
])
OUTPUT_4_triangles = None
OUTPUT_4_Triangulation_Result = None
MESSAGE_4 = "Pas assez de points : le PointSet doit contenir au moins trois points"

#Case 5 - Collinear Points (Failure)
INPUT_5_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': 1.0, 'y': 1.0}, #Index 0
    {'x': 2.0, 'y': 2.0}, #Index 1
    {'x': 3.0, 'y': 3.0} #Index 2
])
OUTPUT_5_triangles = None
OUTPUT_5_Triangulation_Result = None
MESSAGE_5 = "Tous les points sont alignés."

# Case 6 - Grid of 12 points (3x4 grid) -> 6 Triangles
INPUT_6_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': 0.0, 'y': 0.0}, {'x': 5.0, 'y': 0.0}, {'x': 10.0, 'y': 0.0}, {'x': 15.0, 'y': 0.0},  # Indices 0-3
    {'x': 0.0, 'y': 5.0}, {'x': 5.0, 'y': 5.0}, {'x': 10.0, 'y': 5.0}, {'x': 15.0, 'y': 5.0},  # Indices 4-7
    {'x': 0.0, 'y': 10.0}, {'x': 5.0, 'y': 10.0}, {'x': 10.0, 'y': 10.0}, {'x': 15.0, 'y': 10.0} # Indices 8-11
])
OUTPUT_6_Triangulation_Result = {
    'points': INPUT_6_pointSet, 
    'triangles': cast(Triangles_Geom, [
        {'v1': 0, 'v2': 1, 'v3': 4}, {'v1': 4, 'v2': 8, 'v3': 9}, 
        {'v1': 2, 'v2': 4, 'v3': 5}, {'v1': 5, 'v2': 6, 'v3': 10}, 
        {'v1': 2, 'v2': 3, 'v3': 7}, {'v1': 7, 'v2': 10, 'v3': 11}
    ])
}
MESSAGE_6 = "Succes."

# Case 7 - Two clusters of points (15 points) -> 7 Triangles
INPUT_7_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': 2.0, 'y': 2.0}, {'x': 3.0, 'y': 1.0}, {'x': 4.0, 'y': 3.0}, {'x': 1.0, 'y': 4.0}, {'x': 2.5, 'y': 2.5},  
    {'x': 8.0, 'y': 7.0}, {'x': 9.0, 'y': 6.0}, {'x': 10.0, 'y': 8.0}, {'x': 7.0, 'y': 9.0}, {'x': 8.5, 'y': 7.5},  
    {'x': 5.0, 'y': 5.0}, {'x': 6.0, 'y': 4.0}, {'x': 7.0, 'y': 6.0}, {'x': 4.0, 'y': 7.0}, {'x': 5.5, 'y': 5.5}
])
OUTPUT_7_Triangulation_Result = {
    'points': INPUT_7_pointSet, 
    'triangles': cast(Triangles_Geom, [
        {'v1': 0, 'v2': 3, 'v3': 4}, {'v1': 0, 'v2': 1, 'v3': 2}, {'v1': 10, 'v2': 13, 'v3': 14}, 
        {'v1': 2, 'v2': 10, 'v3': 11}, {'v1': 5, 'v2': 12, 'v3': 14}, {'v1': 5, 'v2': 8, 'v3': 9}, 
        {'v1': 5, 'v2': 6, 'v3': 7}
    ])
}
MESSAGE_7 = "Succes."

# Case 8 - Scattered and clustered points (28 points) -> 12 Triangles
INPUT_8_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': 2.0, 'y': 2.0}, {'x': 2.5, 'y': 1.5}, {'x': 1.5, 'y': 2.5}, {'x': 3.0, 'y': 3.0}, {'x': 2.2, 'y': 2.8}, 
    {'x': 8.0, 'y': 5.0}, {'x': 9.0, 'y': 4.0}, {'x': 7.0, 'y': 6.0}, {'x': 10.0, 'y': 5.5}, {'x': 8.5, 'y': 5.5}, 
    {'x': 5.0, 'y': 9.0}, {'x': 5.0, 'y': 10.0}, {'x': 5.0, 'y': 8.0}, {'x': 4.5, 'y': 9.5}, {'x': 5.5, 'y': 8.5}, 
    {'x': 5.0, 'y': 1.0}, {'x': 6.0, 'y': 1.0}, {'x': 4.0, 'y': 1.0}, {'x': 7.0, 'y': 1.0}, {'x': 3.0, 'y': 1.0}, 
    {'x': 15.0, 'y': 15.0}, {'x': -5.0, 'y': -5.0}, {'x': 20.0, 'y': 0.0}, {'x': 0.0, 'y': 20.0}, 
    {'x': 12.0, 'y': 8.0}, {'x': 3.0, 'y': 12.0}, {'x': 14.0, 'y': 3.0}, {'x': 1.0, 'y': 7.0}
])
OUTPUT_8_Triangulation_Result = {
    'points': INPUT_8_pointSet, 
    'triangles': cast(Triangles_Geom, [
        {'v1': 0, 'v2': 2, 'v3': 21}, {'v1': 11, 'v2': 23, 'v3': 25}, {'v1': 12, 'v2': 13, 'v3': 27}, 
        {'v1': 2, 'v2': 3, 'v3': 4}, {'v1': 1, 'v2': 17, 'v3': 19}, {'v1': 10, 'v2': 12, 'v3': 14}, 
        {'v1': 5, 'v2': 7, 'v3': 9}, {'v1': 5, 'v2': 6, 'v3': 8}, {'v1': 8, 'v2': 9, 'v3': 24}, 
        {'v1': 6, 'v2': 8, 'v3': 26}, {'v1': 8, 'v2': 20, 'v3': 24}, {'v1': 22, 'v2': 24, 'v3': 26}
    ])
}
MESSAGE_8 = "Succes."

# Case 9 - Fail Duplicate Points (Two identical points)
INPUT_9_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': 10.0, 'y': 10.0},
    {'x': 5.0, 'y': 5.0},
    {'x': 10.0, 'y': 10.0}, # Duplicate of the first point
    {'x': 0.0, 'y': 10.0},
])
OUTPUT_9_Triangulation_Result = None # Should fail before producing triangles
MESSAGE_9 = "Point Set non valide : au moins deux points sont identiques : tous doivent être différents"


@pytest.fixture(params=[
    #Structure: {case_id, INPUT_pointSet, OUTPUT_triangulation, expected_message}
    {
        "case_id": "1_min_succes_triangle",
        "INPUT_pointSet": INPUT_1_pointSet,
        "OUTPUT_triangulation": OUTPUT_1_Triangulation_Result,
        "expected_message": MESSAGE_1,
    },
    {
        "case_id": "2_square_2_triangles",
        "INPUT_pointSet": INPUT_2_pointSet,
        "OUTPUT_triangulation": OUTPUT_2_Triangulation_Result,
        "expected_message": MESSAGE_2,
    },
    {
        "case_id": "3_Fail_Empty_Input",
        "INPUT_pointSet": INPUT_3_pointSet,
        "OUTPUT_triangulation": OUTPUT_3_Triangulation_Result,
        "expected_message": MESSAGE_3,
    },
    {
        "case_id": "4_Fail_Not_Enough_Points",
        "INPUT_pointSet": INPUT_4_pointSet,
        "OUTPUT_triangulation": OUTPUT_4_Triangulation_Result,
        "expected_message": MESSAGE_4,
    },
    {
        "case_id": "5_Fail_Collinear_Points",
        "INPUT_pointSet": INPUT_5_pointSet,
        "OUTPUT_triangulation": OUTPUT_5_Triangulation_Result,
        "expected_message": MESSAGE_5,
    },
    {
        "case_id": "6_grid_12_points",
        "INPUT_pointSet": INPUT_6_pointSet,
        "OUTPUT_triangulation": OUTPUT_6_Triangulation_Result,
        "expected_message": MESSAGE_6,
    },
    {
        "case_id": "7_two_clusters_15_points",
        "INPUT_pointSet": INPUT_7_pointSet,
        "OUTPUT_triangulation": OUTPUT_7_Triangulation_Result,
        "expected_message": MESSAGE_7,
    },
    {
        "case_id": "8_scattered_28_points",
        "INPUT_pointSet": INPUT_8_pointSet,
        "OUTPUT_triangulation": OUTPUT_8_Triangulation_Result,
        "expected_message": MESSAGE_8,
    },
    {
        "case_id": "9_Fail_Duplicate_Points",
        "INPUT_pointSet": INPUT_9_pointSet,
        "OUTPUT_triangulation": OUTPUT_9_Triangulation_Result,
        "expected_message": MESSAGE_9,
    },
])
def triangulation_geometric_pairs(request):
    """Provide IO pairs and expected error messages for triangulation tests."""
    return request.param

########################################################
########################################################

#Test triangulation compute - Performance test : measure time on a 1000 random point pointSet
N_PERFORMANCE_POINTS = 1000
MAX_COORD = 1000.0

# Generate 1000 random, non-duplicate points within a 1000x1000 square
random.seed(42) # Ensure reproducibility
INPUT_10_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': round(random.uniform(0, MAX_COORD), 2), 
     'y': round(random.uniform(0, MAX_COORD), 2)}
    for _ in range(N_PERFORMANCE_POINTS)
])

# Remove potential duplicates created by rounding (important for the algorithm)
unique_points = []
seen_coords = set()
for p in INPUT_10_pointSet:
    coords = (p['x'], p['y'])
    if coords not in seen_coords:
        seen_coords.add(coords)
        unique_points.append(p)
        
INPUT_10_pointSet = unique_points
N_ACTUAL = len(INPUT_10_pointSet)

OUTPUT_10_Triangulation_Result = {
    'points': INPUT_10_pointSet,
    # Triangles will be calculated by the test itself
    'triangles': cast(Triangles_Geom, []) 
}
MESSAGE_10 = f"Performance test with {N_ACTUAL} unique points."


@pytest.fixture(params=[
    {
        "case_id": "10_Performance_1000_Points",
        "INPUT_pointSet": INPUT_10_pointSet,
        "OUTPUT_triangulation": OUTPUT_10_Triangulation_Result,
        "expected_message": MESSAGE_10,
        "expected_n_points": N_ACTUAL,
    },
], scope='session') # Use session scope for large fixtures
def triangulation_performance_set(request):
    """Provide a large, random point set for performance testing."""
    return request.param


# ------------- Test validate_point_set ---------------#
########################################################

# Case 1 - Valid Point Set
case_1_id = "1_Valid PointSet"
N_1 = 10
_1_PointSet = (
    struct.pack('I', N_1) + 
    struct.pack('f'*N_1*2, 
                0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1,   #Pts 1 to 5
                1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0) #Pts 6 to 10
)
_1_expected_result = None
_1_message = "None"

# Case 2 - Not-valid Point Set
case_2_id = "2_Fail - Length mismatch"
N_2 = 10
_2_PointSet = (
    struct.pack('I', N_2) + 
    struct.pack('fffffff', 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)
)
_2_expected_result = "Exception"
_2_message = "Not-valid PointSet - Point amount mismatch Announced amount"

# Case 3 - Warning in case the PointSet is close to maximal size
case_3_id = "3_Huge_N"
MAX_UNSIGNED_INT_4B = 0xFFFFFFFF
N_3 = MAX_UNSIGNED_INT_4B
_3_PointSet = (
    struct.pack('I', N_3) +
    struct.pack('f',0) # I add this to respect the strucutre, but the actual
                       # test will stop after reading the first 4 bytes 
)
_3_expected_result = "Exception"
_3_message = "Warning - Number of points close to maximum storageble amount"

# Case 4 - Corrupted file (No mathematical meaning (NaN, +-inf))
case_4_id = "4_Corrupted_PointSet"
N_4 = 1
_4_PointSet = (
    struct.pack('I', N_4) + 
    b'\xff\xff\xff\xff\xff\xff\xff\xff'  # 8 bytes de corruption
)
_4_expected_result = "Exception"
_4_message = """Not-valid PointSet - Corrupted content 
                         (NaN, +- inf : no mathematical meaning"""

# Case 5 - Entrée non binaire
case_5_id = "5_Fail - Non-bytes input"
N_5 = None # L'entrée est une chaîne, pas bytes
_5_PointSet = "Ceci est une chaîne de caractères, pas un binaire."
_5_expected_result = "Exception"
_5_message = "Not-valid PointSet - Input must be bytes"

# Case 6 - Too short (less than 4 bytes)
case_6_id = "6_Fail - Too short"
N_6 = None # N is not fully present
_6_PointSet = b'\x01\x02\x03' # Length 3, which is < 4 (HEADER_SIZE)
_6_expected_result = "Exception"
_6_message = "Le PointSet est trop court."


@pytest.fixture(params=[
    {
        "case_id" : case_1_id,
        "PointSet" : _1_PointSet,
        "result" : _1_expected_result,
        "message" : _1_message
    },
    {
        "case_id" : case_2_id,
        "PointSet" : _2_PointSet,
        "result" : _2_expected_result,
        "message" : _2_message
    },
    {
        "case_id" : case_3_id,
        "PointSet" : _3_PointSet,
        "result" : _3_expected_result,
        "message" : _3_message
    },
    {
        "case_id" : case_4_id,
        "PointSet" : _4_PointSet,
        "result" : _4_expected_result,
        "message" : _4_message
    },
    {
        "case_id" : case_5_id,
        "PointSet" : _5_PointSet,
        "result" : _5_expected_result,
        "message" : _5_message
    },
    {
        "case_id" : case_6_id,
        "PointSet" : _6_PointSet,
        "result" : _6_expected_result,
        "message" : _6_message
    },
])
def pointSets(request):
    """Provide PointSets expected resultus for testing validate_point_set."""
    return request.param
########################################################
########################################################
