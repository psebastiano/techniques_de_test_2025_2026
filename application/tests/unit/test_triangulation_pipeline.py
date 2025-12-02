"""Tests unitaires pour la fonction triangulation_pipeline."""

import struct
import uuid
from typing import cast
from unittest.mock import Mock, patch

import pytest
from werkzeug.exceptions import (
    InternalServerError,
)

from application.triangulator_app import triangulation_pipeline
from application.types import PointSet_Geom, Triangles_Geom

VALID_UUID = str(uuid.uuid4())

valid_PointSet = (
    struct.pack('I', 10) + 
    struct.pack('f'*10*2, 
                0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1,   #Pts 1 to 5
                1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0) #Pts 6 to 10
)

valid_pointSet_Geom = cast (PointSet_Geom, [
    {'x': 0.1, 'y': 0.2},
    {'x': 0.3, 'y': 0.4},
    {'x': 0.5, 'y': 0.6},
    {'x': 0.7, 'y': 0.8},
    {'x': 0.9, 'y': 1.0},
    {'x': 1.1, 'y': 1.2},
    {'x': 1.3, 'y': 1.4},
    {'x': 1.5, 'y': 1.6},
    {'x': 1.7, 'y': 1.8},
    {'x': 1.9, 'y': 2.0}
])

mock_triangles_Geom = cast(Triangles_Geom, [
    {'v1': 1, 'v2': 2, 'v3': 3},
    {'v1': 0, 'v2': 1, 'v3': 3},
    {'v1': 0, 'v2': 2, 'v3': 3}
])

mock_triangles = (
    struct.pack('I', 3) + 
    struct.pack('I'*3*3, 
                1, 2, 3, #Triangle 1
                0, 1, 3, #Triangle 2
                0, 2, 3  #Triangle 3
) 
)
Mock_Triangulation_Bytes = (
    valid_PointSet +
    mock_triangles
)

# ------------Test up to validate point set------------
# -> validate point set - Fail Cases (Succes implicit au test suivant. 
#                       Est-ce que je dois le faire aussi ici ?)
# -> decode_binary_to_geometric - Not Executed
# -> triangulation_compute - Not executed
# -> encode_geometric_to_binary - Not executed
@patch('triangulation_pipeline.validate_point_set')
def test_01_triangulation_pipeline_validate_point_set_fail(
    mock_validate_point_set: Mock):
    """Test unitaire pipeline - Echec sur validate_point_set."""
    MOCK_ERROR_MESSAGE = "Validate_point_set FAIL - PointSet Not valid - REASON"
    error = InternalServerError(MOCK_ERROR_MESSAGE)
    
    mock_validate_point_set.side_effect = error
    
    with pytest.raises(InternalServerError) as excinfo:
        triangulation_pipeline(valid_PointSet)
    
    mock_validate_point_set.assert_called_once_with(valid_PointSet)
    assert MOCK_ERROR_MESSAGE in str(excinfo.value)


# ------------Test up to validate point set------------
# -> validate point set - Succes
# -> decode_binary_to_geometric - Fail
# -> triangulation_compute - Not executed
# -> encode_geometric_to_binary - Not executed
@patch('triangulator_app.decode_binary_to_geometric')
@patch('triangulator_app.validate_point_set')
def test_01_triangulation_pipeline_decode_binary_to_geometric_fail(
    mock_validate_point_set: Mock,
    mock_decode_binary_to_geometric: Mock,
    ):
    """Test unitaire pipeline - Echec sur validate_point_set."""
    MOCK_ERROR_MESSAGE = "decode_binary_to_geometric FAIL - REASON"
    error = InternalServerError(MOCK_ERROR_MESSAGE)
    
    mock_validate_point_set.return_value = None #Succes case
    mock_decode_binary_to_geometric.side_effect = error

    with pytest.raises(InternalServerError) as excinfo:
        triangulation_pipeline(valid_PointSet)
    
    mock_validate_point_set.assert_called_once_with(valid_PointSet)
    mock_decode_binary_to_geometric.assert_called_once_with(valid_PointSet)
    assert MOCK_ERROR_MESSAGE in str(excinfo.value)

# ------------Test up to validate point set------------
# -> validate point set - Succes
# -> decode_binary_to_geometric - Succes
# -> triangulation_compute - Fail
# -> encode_geometric_to_binary - Not executed
@patch('triangulator_app.triangulation_compute')
@patch('triangulator_app.decode_binary_to_geometric')
@patch('triangulator_app.validate_point_set')
def test_01_triangulation_pipeline_triangulation_compute_fail(
    mock_validate_point_set: Mock,
    mock_decode_binary_to_geometric: Mock,
    mock_triangulation_compute: Mock
    ):
    """Test unitaire pipeline - Echec sur triangulation compute."""
    MOCK_ERROR_MESSAGE = "Triangulation Compute Fail - REASON"
    error = InternalServerError(MOCK_ERROR_MESSAGE)
    
    mock_validate_point_set.return_value = None #Succes case
    mock_decode_binary_to_geometric.return_value = valid_pointSet_Geom
    mock_triangulation_compute.side_effect = error

    with pytest.raises(InternalServerError) as excinfo:
        triangulation_pipeline(valid_PointSet)
    
    mock_validate_point_set.assert_called_once_with(valid_PointSet)
    mock_decode_binary_to_geometric.assert_called_once_with(valid_PointSet)
    mock_triangulation_compute.assert_called_once_with(valid_pointSet_Geom)
    assert MOCK_ERROR_MESSAGE in str(excinfo.value)

# ------------Test up to validate point set------------
# -> validate point set - Succes
# -> decode_binary_to_geometric - Succes
# -> triangulation_compute - Succes
# -> encode_geometric_to_binary - Succes and Fail
@pytest.mark.parametrize("case_id, http_exception_type, result, message", [
    #Cas 200 - Success
    ("Succes_200", None, Mock_Triangulation_Bytes, None),
    #Cas 500 - Internal Server Error
    ("Fail 500", InternalServerError, None, "encode_geometric_to_binary Fail - Reason"),
])
@patch('triangulator_app.encode_geometric_to_binary')
@patch('triangulator_app.triangulation_compute')
@patch('triangulator_app.decode_binary_to_geometric')
@patch('triangulator_app.validate_point_set')
def test_01_triangulation_pipeline_(
    mock_validate_point_set: Mock,
    mock_decode_binary_to_geometric: Mock,
    mock_triangulation_compute: Mock,
    mock_encode_geometric_to_binary: Mock,
    case_id,
    http_exception_type,
    result,
    message
    ):
    """Test unitaire pipeline - Succes OU Echec sur encode_geometric_to_binary."""  
    mock_validate_point_set.return_value = None #Succes case
    mock_decode_binary_to_geometric.return_value = valid_pointSet_Geom #Succes case
    mock_triangulation_compute.return_value =  mock_triangles_Geom#Succe case

    if case_id == "Success_200":
        mock_encode_geometric_to_binary.return_value = result
        
        actual_result = triangulation_pipeline(valid_PointSet)
        assert actual_result == result 
    else :
        error = http_exception_type(message)
        mock_encode_geometric_to_binary.side_effect = error

        with pytest.raises(InternalServerError) as excinfo:
            triangulation_pipeline(valid_PointSet)
        assert message in str(excinfo.value)

    mock_validate_point_set.assert_called_once_with(valid_PointSet)
    mock_decode_binary_to_geometric.assert_called_once_with(valid_PointSet)
    mock_triangulation_compute.assert_called_once_with(valid_pointSet_Geom)
    mock_encode_geometric_to_binary.assert_called_once_with(mock_triangles_Geom)
    