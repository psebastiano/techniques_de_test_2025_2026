"""Tests unitaires pour la fonction decode_binary_to_geometric.

Vérifie si la conversion est correcte pour un ensembe d'entrée différentes.
"""

from application.triangulator_app import encode_triangulation_result_to_binary


def test_01_encode_triangulation_result_to_binary(
        triangulations_geometric_binary_pairs
    ):
    """Vérifie que la fonction sous test ne retourne rien si uudi valide."""
    expected = triangulations_geometric_binary_pairs["encoded_binary_expected"]
    geometric = triangulations_geometric_binary_pairs["geometric_input"]
    
    actual = encode_triangulation_result_to_binary(geometric)
    
    assert actual == expected