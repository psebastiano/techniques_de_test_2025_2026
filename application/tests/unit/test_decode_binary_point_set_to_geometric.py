"""Tests unitaires pour la fonction decode_binary_to_geometric.

Vérifie si la conversion est correcte pour un ensembe d'entrée différentes.
"""

from application.triangulator_app import decode_binary_point_set_to_geometric


def test_01_decode_binary_point_set_to_geometric(point_set_binary_geometric_pairs):
    """Vérifie que la fonction sous test ne retourne rien si uudi valide."""
    expected = point_set_binary_geometric_pairs["decoded_geometric"]
    binary = point_set_binary_geometric_pairs["encoded_binary"]

    tol = 0.001
    actual = decode_binary_point_set_to_geometric(binary, tol)
    
    assert actual == expected