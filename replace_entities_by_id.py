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

# Inverser les lignes d'écoulement dans la couche source
with edit(source_layer):
    for feature in source_layer.getFeatures():
        # Récupérer la géométrie de l'entité
        geom = feature.geometry()
        # Inverser les lignes d'écoulement
        geom.reverse()
        # Mettre à jour la géométrie de l'entité
        source_layer.changeGeometry(feature.id(), geom)


# Récupérer les identifiants des entités dans la couche source
identifiants = []
for feature in source_layer.getFeatures():
    identifiants.append(feature['cleabs'])

# Remplacer les entités correspondantes dans la couche cible
with edit(cible_layer):
    for feature in cible_layer.getFeatures(QgsFeatureRequest().setFilterFids(identifiants)):
        cible_layer.deleteFeature(feature.id())
    for feature in source_layer.getFeatures(QgsFeatureRequest().setFilterFids(identifiants)):
        cible_layer.addFeature(feature, QgsFeatureRequest().setNoAttributesCheck(True))

# Sauvegarder les changements dans la couche cible
QgsProject.instance().write()
