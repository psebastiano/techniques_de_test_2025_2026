"""Fichier de configuration de Pytest Défintion des fixtures."""
import http.client
import struct
from typing import cast
from unittest.mock import Mock, patch

import pytest

from application.types import PointSet_Geom, Triangles_Geom, Triangulation_Result


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
    "FFFFFFFF-FFFF-FFFF-FFFF"   # Not long enough
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
        "encoded_binary": struct.pack('Iffff', 2, 5.5, 12.3, 1, 13),
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
                {'v1': 0, 'v2': 1, 'v4': 2},
                
            ]
        }),
        "encoded_binary_expected":(
            struct.pack('I', 3) + 
            struct.pack('ffffff', 0.0, 0.0, 1.0, 0.0, 0.0, 1.0) + 
            struct.pack('I', 1) + 
            struct.pack('III', 0, 1, 2)
            
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
    {'x': 0.0, 'y': 0.0}, #Index 
    {'x': 10.0, 'y': 0.0}, #Index 
    {'x': 5.0, 'y': 10.0}, #Index 
])
OUTPUT_1_triangles = Triangles_Geom = cast(Triangles_Geom, [
    {'v1': 0, 'v2': 1, 'v3': 2}
])
OUTPUT_1_Triangulation_Result = {
    'points' : INPUT_1_pointSet,
    'triangles' : OUTPUT_1_triangles
}
MESSAGE_1 = "Success."

# Case 2 - A square (4 points, 2 triangles)
INPUT_2_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': 0.0, 'y': 0.0}, #Index 
    {'x': 10.0, 'y': 0.0}, #Index 
    {'x': 10.0, 'y': 10.0}, #Index
    {'x': 0.0, 'y': 10.0}, #Index 
])
# ??? Input 2 can make two valid outputs ... how to check ???
OUTPUT_2_triangles = cast(Triangles_Geom, [ 
    {'v1': 0, 'v2': 1, 'v3': 2},
    {'v1': 0, 'v2': 2, 'v3': 3}
])
OUTPUT_2_Triangulation_Result = {
    'points' : INPUT_2_pointSet,
    'triangles' : OUTPUT_2_triangles
}
MESSAGE_2 = "Success."

# Case 3 - Empty Input - Should raise an error
INPUT_3_pointSet: PointSet_Geom = cast(PointSet_Geom, [])
OUTPUT_3_triangles = None
OUTPUT_3_Triangulation_Result = None
MESSAGE_3 = "Empty input."

# Case 4 - Too few points - Should raise an error
INPUT_4_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': 1.0, 'y': 1.0}, #Index 
    {'x': 2.0, 'y': 2.0} #Index 
])
OUTPUT_4_triangles = None
OUTPUT_4_Triangulation_Result = None
MESSAGE_4 = "Not enough Points : Input must contain at least 3 points."

#Case 5 - Collinear Points (Failure)
INPUT_5_pointSet: PointSet_Geom = cast(PointSet_Geom, [
    {'x': 1.0, 'y': 1.0}, #Index 
    {'x': 2.0, 'y': 2.0}, #Index 
    {'x': 3.0, 'y': 3.0} #Index
])
OUTPUT_5_triangles = None
OUTPUT_5_Triangulation_Result = None
MESSAGE_5 = "Collinear Points."

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
    }
])
def triangulation_geometric_pairs(request):
    """Provide IO pairs and expected error messages for triangulation tests."""
    return request.param

########################################################
########################################################



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
_1_expected_result = "None"
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

# Case 4 - Corrupted file
case_4_id = "4_Corrupted_PointSet"
N_4 = 1
_4_PointSet = (
    struct.pack('I', N_4) + 
    b'\xff\xff\xff\xff\xff\xff\xff\xff'  # 8 bytes de corruption
)
_4_expected_result = "Exception"
_4_message = "Not-valid PointSet - Corrupted content"
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
])
def pointSets(request):
    """Provide PointSets expected resultus for testing validate_point_set."""
    return request.param
########################################################
########################################################
