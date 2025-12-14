"""------------Structure de données internes au Triangulateur-------------."""
from typing import TypeAlias

# Point Set au format géométrique
PointGeom: TypeAlias = dict[str, float]
"""
Cette structure permet de stocler un point.
{'x' : , 'y' :}
"""

PointSet_Geom: TypeAlias = list[PointGeom]
"""
Ceci est l'entrée pour l'algorithme de triangulation. 
Une liste de dictionnaire, chacun représentant un point comme float.
"""

Triangle_Indices : TypeAlias = dict[str, int]
"""
Cette structure permet de stocker un triangle.
Ces sommets sont nommées : v1, v2, v3
Il sont associé à l'index du point qu'il représente dans une liste de points 
"""
Triangles_Geom: TypeAlias = list[Triangle_Indices]
"""
Cette structure permet de stocker plusieurs triangles. 
"""

Triangulation_Result: TypeAlias = dict[str, PointSet_Geom | Triangles_Geom]