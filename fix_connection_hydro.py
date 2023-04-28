# Importer les bibliothèques nécessaires
from qgis.core import QgsProject, QgsVectorLayer, QgsFeatureRequest


# Chemins vers les fichiers GPKG
source_gpkg = 'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/fct/referentiel_hydrographique.gpkg|layername=troncon_hydrographique_conn'
cible_gpkg = 'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/fct/referentiel_hydrographique.gpkg|layername=2_troncon_hydrographique_cours_d_eau_corr_conn_inv'

# Charger les couches sources et cibles
source_layer = QgsVectorLayer(source_gpkg, 'troncon_hydrographique_conn', 'ogr')
cible_layer = QgsVectorLayer(cible_gpkg, '2_troncon_hydrographique_cours_d_eau_corr_conn_inv', 'ogr')

# Vérifier que les couches ont bien été chargées
if not source_layer.isValid() or not cible_layer.isValid():
    print('Une des couches n\'a pas été chargée correctement')
    exit()

# Récupérer les identifiants des entités dans la couche source
identifiants = []
for feature in source_layer.getFeatures():
    identifiants.append("'" + feature['cleabs'] + "'") # Ajouter des guillemets autour de la valeur de l'identifiant

# regarder si des identifiants sont déjà présent dans la couche source
nomodif = []
for feature in cible_layer.getFeatures(QgsFeatureRequest().setFilterExpression('"cleabs" IN ({})'.format(','.join(identifiants)))):
    # print(feature['cleabs'] + ' already exist')
    nomodif.append("'" + feature['cleabs'] + "'")
nouvelle_liste = [id for id in identifiants + nomodif if id not in identifiants or id not in nomodif]
if not nomodif:
    print('Features id to check, already in the layer to fix ' + str(nomodif))
else :
    print('no features from the layer to fix, no check needed')

# ajouter uniquement les entités qui ne sont pas déjà dans la couche source
with edit(cible_layer):
    # récupérer les entités de la couche source 
    for feature in source_layer.getFeatures(QgsFeatureRequest().setFilterExpression('"cleabs" IN ({})'.format(','.join(nouvelle_liste)))):
        fet = QgsFeature(feature)
        fet['fid'] = None
        cible_layer.addFeatures([fet])
        print(fet['cleabs'] + ' line added')

