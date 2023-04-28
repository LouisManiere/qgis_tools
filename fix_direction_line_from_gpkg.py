# Importer les bibliothèques nécessaires
from qgis.core import QgsProject, QgsVectorLayer, QgsFeatureRequest


# Chemins vers les fichiers GPKG
source_gpkg = 'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/fct/referentiel_hydrographique.gpkg|layername=troncon_hydrographique_corr_dir_ecoulement'
cible_gpkg = 'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/fct/referentiel_hydrographique.gpkg|layername=1_troncon_hydrographique_cours_d_eau_corr_conn_inv'

# Charger les couches sources et cibles
source_layer = QgsVectorLayer(source_gpkg, 'troncon_hydrographique_corr_dir_ecoulement', 'ogr')
cible_layer = QgsVectorLayer(cible_gpkg, '1_troncon_hydrographique_cours_d_eau_corr_conn_inv', 'ogr')

# Vérifier que les couches ont bien été chargées
if not source_layer.isValid() or not cible_layer.isValid():
    print('Une des couches n\'a pas été chargée correctement')
    exit()

# Récupérer les identifiants des entités dans la couche source
identifiants = []
for feature in source_layer.getFeatures():
    identifiants.append("'" + feature['cleabs'] + "'") # Ajouter des guillemets autour de la valeur de l'identifiant

# Inverse les lignes d'écoulement pour les entités de source_layer
with edit(cible_layer):
    for feature in cible_layer.getFeatures(QgsFeatureRequest().setFilterExpression('"cleabs" IN ({})'.format(','.join(identifiants)))):
        # Récupérer la géométrie de l'entité
        geom = feature.geometry()
        lines = geom.asPolyline()
        # Inverser les lignes d'écoulement
        lines.reverse()
        newgeom = QgsGeometry.fromPolylineXY(lines)
        # Mettre à jour la géométrie de l'entité
        cible_layer.changeGeometry(feature.id(), newgeom)
