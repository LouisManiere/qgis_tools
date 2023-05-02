# Importer les bibliothèques nécessaires
from qgis.core import QgsProject, QgsVectorLayer, QgsFeatureRequest


# Chemins vers les fichiers GPKG
source_gpkg = 'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/fct/referentiel_hydrographique.gpkg|layername=troncon_hydrographique_cours_d_eau_modif_geom'
cible_gpkg = 'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/fct/referentiel_hydrographique.gpkg|layername=3_troncon_hydrographique_cours_d_eau_corr_conn_inv'

# Charger les couches sources et cibles
source_layer = QgsVectorLayer(source_gpkg, 'troncon_hydrographique_cours_d_eau_modif_geom', 'ogr')
cible_layer = QgsVectorLayer(cible_gpkg, '3_troncon_hydrographique_cours_d_eau_corr_conn_inv', 'ogr')

# Vérifier que les couches ont bien été chargées
if not source_layer.isValid() or not cible_layer.isValid():
    print('Une des couches n\'a pas été chargée correctement')
    exit()

# Récupérer les identifiants des entités dans la couche source
identifiants = []
for feature in source_layer.getFeatures():
    identifiants.append("'" + feature['cleabs'] + "'") # Ajouter des guillemets autour de la valeur de l'identifiant

# mise à jour de la géométrie de la couche cible aec la couche source
with edit(cible_layer):
    for feature in cible_layer.getFeatures(QgsFeatureRequest().setFilterExpression('"cleabs" IN ({})'.format(','.join(identifiants)))):
        # récupérer et modifier l'identifiant de l'entité en cours de la couche cible
        id = "'" + feature['cleabs'] +"'"
        # récupérer la géométrie de la source correspondant à l'identifiant de l'entité de la couche cible
        geom = next(source_layer.getFeatures(QgsFeatureRequest().setFilterExpression('"cleabs" IN ({})'.format(id)))).geometry()
        # Mettre à jour la géométrie de l'entité
        cible_layer.changeGeometry(feature.id(), geom)
        print(feature['cleabs'] + ' line modified')
