"""Tests unitaires pour la fonction triangulation compute."""
import time

import pytest

from application.custom_types import Triangulation_Result
from application.triangulator_app import triangulation_compute


def test_01_triangulation_compute(triangulation_geometric_pairs):
    """Tests the tringulation_compute function using explicit flow control."""
    #Unpack test data
    case_id = triangulation_geometric_pairs['case_id']
    input_geom = triangulation_geometric_pairs['INPUT_pointSet']
    expected_result = triangulation_geometric_pairs['OUTPUT_triangulation']
    expected_message = triangulation_geometric_pairs['expected_message']

    if case_id in ["1_min_succes_triangle", "2_square_2_triangles", "6_grid_12_points",
                   "7_two_clusters_15_points", "8_scattered_28_points"]:
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

    else:
        with pytest.raises(Exception) as excinfo:
            triangulation_compute(input_geom)
        assert expected_message in str(excinfo)

@pytest.mark.performance
def test_02_performance_triangulation_compute(triangulation_performance_set):
    """Mesure le temps d'execution de triangulation_compute pour un PointSet de mille points aléatoires."""
    point_set = triangulation_performance_set["INPUT_pointSet"]
    expected_n = triangulation_performance_set["expected_n_points"]
    
    start_time = time.time()
    
    # Execute the function under test
    result = triangulation_compute(point_set)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Assert that the function ran without throwing an exception (Success)
    assert result is not None
    
    # Print the performance metric (Ruff compliant f-string)
    print(
        f"\nPerformance Result: {expected_n} points triangulated in "
        f"{duration:.4f} seconds."
    )
    assert duration < 5.0