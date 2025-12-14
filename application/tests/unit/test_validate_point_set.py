"""Tests unitaires pour la fonction validate_point_set.

Vérifie l'intégrité du point set.
"""

import pytest

from application.triangulator_app import validate_point_set


def test_01_validate_point_set(pointSets):
    """Validate the itegrity of a PointSet."""
    case_id = pointSets["case_id"]
    PointSet = pointSets["PointSet"]
    expected_result = pointSets["result"]
    expected_message = pointSets["message"]

    if case_id == "1_Valid PointSet" :
        actual_result = validate_point_set(PointSet)
        print("actual_result : ", actual_result)
        print("expected_result : ", expected_result)
        
        assert expected_result == actual_result #None expected
    else:
        with pytest.raises(Exception) as excinfo:
            validate_point_set(PointSet)
        assert expected_message.strip() in str(excinfo.value).strip()