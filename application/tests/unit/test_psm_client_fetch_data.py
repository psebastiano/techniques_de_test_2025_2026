"""Tests unitaires pour la fonction psm client fetch data."""
import json

from application.triangulator_app import psm_client_fetch_data

# Cas 0 - Succes
# Cas 1 - Not Found
# Cas 2 - Service unavailable

# mock of /triangulation/{pointSetId} served by PSM

TEST_POINT_SET_ID = "a1b2c3d4-e5f6-7890-1234-567890abcdef"

def test_01_psm_client_fetch_data(mock_psm_connection):
    """Tests psm_client_fetch_data across all API scenarios (200, 4xx, 5xx, ... )."""
    uuid = TEST_POINT_SET_ID
    mock_instance = mock_psm_connection
    expected_status = mock_instance.status_code
    expected_body = mock_instance.body

    response = psm_client_fetch_data(uuid)

    assert response.status == expected_status

    if expected_status == 200: #Succes
        assert dict(response.getheaders())['Content-Type'] == 'application/octet-stream'
        
        body = response.read()
        assert body == expected_body
        assert isinstance(body, bytes)
    else: #Failure
        assert dict(response.getheaders())['Content-Type'] == 'application/json'
        
        body_bytes = response.read()
        assert body_bytes == expected_body

        expected_json = json.loads(expected_body.decode('utf-8'))
        response_json = json.loads(body_bytes.decode('utf-8'))
        
        assert 'error' in response_json
        assert response_json['error'] == expected_json['error']
