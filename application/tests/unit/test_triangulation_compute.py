"""Tests unitaires pour la fonction triangulation compute."""
import pytest

from application.triangulator_app import triangulation_compute
from application.types import Triangulation_Result


def test_01_triangulation_compute(triangulation_geometric_pairs):
    """Tests the tringulation_compute function using explicit flow control."""
    #Unpack test data
    case_id = triangulation_geometric_pairs['case_id']
    input_geom = triangulation_geometric_pairs['INPUT_pointSet']
    expected_result = triangulation_geometric_pairs['OUTPUT_triangulation']
    expected_message = triangulation_geometric_pairs['expected_message']

    if case_id in ["1_min_succes_triangle", "2_square_2_triangles"]:
        actual_result: Triangulation_Result = triangulation_compute(input_geom)
        assert actual_result['points'] == expected_result['points']

        #Normalization - Vertes sorting in triangles
        expected_triangles_nomalized = sorted([
            tuple(sorted(t.values())) for t in expected_result['triangles']
        ])

        actual_triangles_nomalized = sorted([
            tuple(sorted(t.values())) for t in actual_result['triangles']
        ])
        assert actual_triangles_nomalized == expected_triangles_nomalized


    elif case_id in ["3_Fail_Empty_Input", "4_Fail_Not_Enough_Points",
                     "5_Fail_Collinear_Points"]:
        with pytest.raises(Exception) as excinfo:
            triangulation_compute(input_geom)
        assert expected_message in str(excinfo)
    else:
        pytest.fail(f"Test setup error : Unknow case_id '{case_id}' encountered.")
