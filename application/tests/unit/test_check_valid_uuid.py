"""Tests unitaires pour la fonction check_valid_uuid.

Vérifie la conformité du format de l'UUID pour intercepter les erreurs HTTP 400.
"""

import pytest

from application.triangulator_app import check_valid_uuid


def test_01_cas_succes_uuid_valide(uuid_str_valide: str):
    """Vérifie que la fonction sous test ne retourne rien si uuid valide."""
    result = check_valid_uuid(uuid_str_valide)
    assert result is None

def test_02_cas_echec_uuid_unvalide(uuid_str_non_valide: str):
    """Vérifie que la fonction sous test retourne une erreur si uuid non valide."""
    with pytest.raises(ValueError):
        check_valid_uuid(uuid_str_non_valide)