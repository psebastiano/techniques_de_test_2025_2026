"""Module pour le test du serveur Flask."""

from unittest.mock import patch

import pytest
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound, ServiceUnavailable

from application.triangulator_app import triangulator_app


@pytest.fixture
def client():
    """Set up the test client for the application."""
    # Use Flask's testing environment setup
    triangulator_app.config['TESTING'] = True
    with triangulator_app.test_client() as client:
        yield client

def test_triangulation_route_success(client):
    """Teste le succes (200 OK) de la route /triangulation/{id}.
    
    Mocks getTriangulation to return dummy binary data.
    """
    mock_uuid = "a0000000-0000-0000-0000-000000000001"
    expected_data = b"MOCK BINARY TRIANGULATION DATA"

    # Patch the getTriangulation function to control its return value
    with patch('application.triangulator_app.getTriangulation', return_value=expected_data) as mock_func:
        # Simulate a GET request to the route
        response = client.get(f'/triangulation/{mock_uuid}')

        # Assertions
        assert response.status_code == 200
        assert response.content_type == 'application/octet-stream'
        assert response.data == expected_data
        
        # Verify that our core function was called exactly once with the correct ID
        mock_func.assert_called_once_with(mock_uuid)

def test_triangulation_route_invalid_uuid(client):
    """Test erreur 400 Bad Request pour un pointSet invalide."""
    invalid_id = "not-a-uuid"

    # Patch the function to simulate the 400 error coming from validation
    with patch('application.triangulator_app.getTriangulation', side_effect=BadRequest) as mock_func:
        response = client.get(f'/triangulation/{invalid_id}')

        # Assertions
        assert response.status_code == 400
        assert response.content_type == 'application/json' 
        # Optionally, check for specific error message in the JSON body
        # assert b"Bad Request" in response.data 
        
        mock_func.assert_called_once_with(invalid_id)

def test_triangulation_route_not_found(client):
    """Teste le cas 404 Not Found. Simule un échec du PSM."""   
    unknown_id = "b0000000-0000-0000-0000-000000000002"

    # Patch the function to simulate the 404 error
    with patch('application.triangulator_app.getTriangulation', side_effect=NotFound) as mock_func:
        response = client.get(f'/triangulation/{unknown_id}')

        # Assertions
        assert response.status_code == 404
        assert response.content_type == 'application/json' 
        
        mock_func.assert_called_once_with(unknown_id)

def test_triangulation_route_internal_error(client):
    """Teste le cas 500 Internal Server Error. Simule un échec de l'algorithme de triangulation."""
    error_id = "c0000000-0000-0000-0000-000000000003"
    
    # Patch the function to simulate the 500 error coming from the core logic
    with patch('application.triangulator_app.getTriangulation', side_effect=InternalServerError) as mock_func:
        response = client.get(f'/triangulation/{error_id}')

        # Assertions
        assert response.status_code == 500
        assert response.content_type == 'application/json' 
        
        mock_func.assert_called_once_with(error_id)

def test_triangulation_route_service_unavailable(client):
    """Teste le cas 503 Service Unavailable. Simule une impossibilité de communiquer avec le PSM (ex: timeout)."""
    unavailable_id = "d0000000-0000-0000-0000-000000000004"
    
    # Patch the function to simulate the 503 error coming from the PSM communication
    with patch('application.triangulator_app.getTriangulation', side_effect=ServiceUnavailable) as mock_func:
        response = client.get(f'/triangulation/{unavailable_id}')

        # Assertions
        assert response.status_code == 503
        assert response.content_type == 'application/json' 
        
        mock_func.assert_called_once_with(unavailable_id)