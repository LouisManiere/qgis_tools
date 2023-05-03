"""
Add the features from the source_layer to the cible_layer
"""
from qgis.core import QgsVectorLayer, QgsFeatureRequest


# path to pgkg files
source_gpkg = 'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/fct/referentiel_hydrographique.gpkg|layername=troncon_hydrographique_conn'
cible_gpkg = 'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/fct/referentiel_hydrographique.gpkg|layername=6_troncon_hydrographique_cours_d_eau_corr_conn_inv'

# load layers
source_layer = QgsVectorLayer(source_gpkg, 'troncon_hydrographique_conn', 'ogr')
cible_layer = QgsVectorLayer(cible_gpkg, '6_troncon_hydrographique_cours_d_eau_corr_conn_inv', 'ogr')

# check if layers are valid
if not source_layer.isValid() or not cible_layer.isValid():
    print('Une des couches n\'a pas été chargée correctement')

# get Ids from source_layer
identifiants = []
for feature in source_layer.getFeatures():
    identifiants.append("'" + feature['cleabs'] + "'")

# check if there are already in the cible_layer
nomodif = []
for feature in cible_layer.getFeatures(QgsFeatureRequest().setFilterExpression('"cleabs" IN ({})'.format(','.join(identifiants)))):
    nomodif.append("'" + feature['cleabs'] + "'")
nouvelle_liste = [id for id in identifiants + nomodif if id not in identifiants or id not in nomodif]
if not nomodif:
    print('Features id to check, already in the layer to fix ' + str(nomodif))
else :
    print('no features from the layer to fix, no check needed')

# Add the features not present in the cible_layer
with edit(cible_layer):
    # get features from the source_layer
    for feature in source_layer.getFeatures(QgsFeatureRequest().setFilterExpression('"cleabs" IN ({})'.format(','.join(nouvelle_liste)))):
        fet = QgsFeature(feature)
        fet['fid'] = None
        cible_layer.addFeatures([fet])
        print(fet['cleabs'] + ' line added')

