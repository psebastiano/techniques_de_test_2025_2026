"""Tests unitaires pour la fonction validate_point_set.

Vérifie l'intégrité du point set.
"""

import pytest

from application.triangulator_app import validate_point_set


def test_01_validate_point_set(pointSets):
    """Validate the itegritu of a PointSet."""
    case_id = pointSets["case_id"]
    PointSet = pointSets["PointSet"]
    expected_result = pointSets["result"]
    expected_message = pointSets["message"]

    if case_id == "1_Valid PointSet" :
        actual_result = validate_point_set(PointSet)
        assert expected_result == actual_result #None expected
    elif case_id in ["2_Fail - Length mismatch", "3_Huge_N", 
                     "4_Corrupted_PointSet"]:
        with pytest.raises(Exception) as excinfo:
            validate_point_set(PointSet)
        assert expected_message in str(excinfo)
    else:
        pytest.fail(f"Test setup error : Unknow case_id '{case_id}' encountered.")