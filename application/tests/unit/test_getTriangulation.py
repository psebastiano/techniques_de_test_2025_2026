"""Tests unitaires pour la fonction handler triangulation_get."""

import struct
import uuid
from unittest.mock import Mock, patch

import pytest
from werkzeug.exceptions import (
    BadRequest,
    InternalServerError,
    NotFound,
    ServiceUnavailable,
)

from application.triangulator_app import getTriangulation

# ------------Test up to check valid uuid------------
# -> check valid uuid - Fail Cases (Succes implicit au test suivant. 
#                       Est-ce que je dois le faire aussi ici ?)
# -> psd fetch client data - Not executed
# -> triangulation_pipeline - Not executed

@patch('application.triangulator_app.check_valid_uuid')
def test_01_getTriangulation_check_uuid_fail(mock_check_valid_uuid: Mock):
    """Tests unitaires orchestrateur - Cas d'échec sur check_valid_uuid."""
    INVALID_ID = "not_a_uuid"
    MOCK_ERROR_MESSAGE = "Le PointSetId doit être un UUID valide"

    mock_check_valid_uuid.side_effect = ValueError(MOCK_ERROR_MESSAGE)

    with pytest.raises(BadRequest) as excinfo:
        getTriangulation(INVALID_ID)
    
    mock_check_valid_uuid.assert_called_once_with(INVALID_ID)
    assert MOCK_ERROR_MESSAGE in str (excinfo.value)
######################################################

# ------------Test up to psd fetch client data------------
# -> check valid uuid - Success
# -> psd fetch client data - Fail cases (Succes implicit au test suivant.
#                            Même question que plus haut.)
# -> triangulation_pipeline - Not executed

VALID_UUID = str(uuid.uuid4())
@pytest.mark.parametrize("case_id, http_exception_type, error_message", [
    #Cas 400 - PSM answer 400 to fetch_data
    ("Fail_400", BadRequest, "PSM : uuid format not valid"),
    #Cas 404 - PSM answer 404 to fetch_data
    ("Fail 404", NotFound, "PSM : Coudn't find the requested PointSet"),
    #Cas 503 - PSM answer 503 to fetch_data
    ("Fail 500", ServiceUnavailable, "PSM is not responding"),
])
@patch('application.triangulator_app.triangulation_pipeline')
@patch('application.triangulator_app.psm_client_fetch_data')
@patch('application.triangulator_app.check_valid_uuid')
def test_02_getTriangulation_fetch_data_fail(
    mock_check_uuid: Mock,
    mock_fetch_data: Mock,
    mock_triangulation_pipeline: Mock,
    case_id,
    http_exception_type,
    error_message
):
    """Tests unitaires orchestrateur - Cas d'échec sur psm fetch client data."""
    #First step is okay
    mock_check_uuid.return_value = None
    
    #Set up de l'erreur attendue deupuis PSM
    mock_fetch_data.side_effect = http_exception_type

    with pytest.raises(http_exception_type) as excinfo:
        getTriangulation(VALID_UUID)
    
    #Verifications
    mock_check_uuid.assert_called_once_with(VALID_UUID)
    mock_fetch_data.assert_called_once_with(VALID_UUID)
    mock_triangulation_pipeline.assert_not_called()

    assert error_message in str(excinfo.value)
###########################################################

# ------------Test up to triangulation pipeline------------
# -> check valid uuid - Success
# -> psd fetch client data - Success
# -> triangulation_pipeline - Succes and Fail (500 - Internal Server Error)
VALID_UUID = str(uuid.uuid4())
valid_PointSet = (
    struct.pack('I', 10) + 
    struct.pack('f'*10*2, 
                0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1,   #Pts 1 to 5
                1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0) #Pts 6 to 10
)
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
@pytest.mark.parametrize("case_id, http_exception_type, result, message", [
    #Cas 200 - Success
    ("Succes_200", None, Mock_Triangulation_Bytes, None),
    #Cas 500 - Internal Server Error
    ("Fail 500", InternalServerError, None, "Triangulation Failed"),
])
@patch('application.triangulator_app.triangulation_pipeline')
@patch('application.triangulator_app.psm_client_fetch_data')
@patch('application.triangulator_app.check_valid_uuid')
def test_03_getTriangulation_triangulation_pipeline_fail(
    mock_check_uuid: Mock,
    mock_fetch_data: Mock,
    mock_triangulation_pipeline: Mock,
    case_id,
    http_exception_type,
    result,
    message
):
    """Tests unitaires orchestrateur - Cas d'échec sur triangulation_pipeline."""
    #First step is okay
    mock_check_uuid.return_value = None
    
    #Fetch data returns a valid pointSet
    mock_fetch_data.return_value = valid_PointSet

    #Verify returned value is of type Triangulation_Result
    #Si succes : - la valeur retourné est Triangulation_Result
    #Si echec : - la valeur retourné est None + Erreur 500
    if case_id == "Succes_200":
        mock_triangulation_pipeline.return_value = result
        
        triangulation_result = getTriangulation(VALID_UUID)
        assert triangulation_result == result
    
    else:
        mock_triangulation_pipeline.side_effect = RuntimeError(message)

        with pytest.raises(http_exception_type) as excinfo:
            getTriangulation(VALID_UUID)
        assert message in str(excinfo.value)
    
    #Verifications
    mock_check_uuid.assert_called_once_with(VALID_UUID)
    mock_fetch_data.assert_called_once_with(VALID_UUID)
    mock_triangulation_pipeline.assert_called_once_with(valid_PointSet)
###########################################################