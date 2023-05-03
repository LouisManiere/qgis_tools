"""
From the ids of a gpkg layer (source_layer), select the features in the cible_layer and reverse the line direction.
"""

from qgis.core import QgsVectorLayer, QgsFeatureRequest


# Paths to the GPKG files
source_gpkg = 'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/fct/referentiel_hydrographique.gpkg|layername=troncon_hydrographique_corr_dir_ecoulement'
cible_gpkg = 'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/fct/referentiel_hydrographique.gpkg|layername=3_troncon_hydrographique_cours_d_eau_corr_conn_inv'

# Load the source and target layers
source_layer = QgsVectorLayer(source_gpkg, 'troncon_hydrographique_corr_dir_ecoulement', 'ogr')
cible_layer = QgsVectorLayer(cible_gpkg, '3_troncon_hydrographique_cours_d_eau_corr_conn_inv', 'ogr')

# Check that the layers were loaded correctly
if not source_layer.isValid() or not cible_layer.isValid():
    print('Une des couches n\'a pas été chargée correctement')

# Get the IDs of the features in the source layer
identifiants = []
for feature in source_layer.getFeatures():
    identifiants.append("'" + feature['cleabs'] + "'")

# Reverse the flow direction for the features in the target layer
with edit(cible_layer):
    for feature in cible_layer.getFeatures(QgsFeatureRequest().setFilterExpression('"cleabs" IN ({})'.format(','.join(identifiants)))):
        # Get the geometry of the feature
        geom = feature.geometry()
        lines = geom.asPolyline()
        # Reverse the flow direction
        lines.reverse()
        newgeom = QgsGeometry.fromPolylineXY(lines)
        # Update the geometry of the feature
        cible_layer.changeGeometry(feature.id(), newgeom)
        print(feature['cleabs'] + ' line direction inversed')
