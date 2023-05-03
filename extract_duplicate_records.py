
"""
Add the features from the source_layer to the cible_layer
"""
from qgis.core import QgsVectorLayer, QgsVectorFileWriter

# names
# inputs
troncon_hydro_name = '4_troncon_hydrographique_cours_d_eau_corr_conn_inv'
# outputs
duplicate_name = 'troncon_hydrographique_corr_duplicate'


# pgkg file exutoire
referentiel_hydro_gpkg = 'C:/Users/lmanie01/Documents/Projets/Mapdo/Data/fct/referentiel_hydrographique.gpkg'


# path to pgkg files
troncon_hydro_layer = f"{referentiel_hydro_gpkg}|layername={troncon_hydro_name}"
duplicate_layer = f"{referentiel_hydro_gpkg}|layername={duplicate_name}"

# load layers
troncon_hydro = QgsVectorLayer(troncon_hydro_layer, troncon_hydro_name, 'ogr')

# check if layers are valid
if not troncon_hydro.isValid():
    print('La couche n\'a pas été chargée correctement')

# troncon_hydro.selectByExpression("count(1,\"cleabs\")>1")


def select_features_with_duplicates(layer, reference_field: str) -> None:
    """
    Selects features with duplicates in the reference field
    :param layer_name: name of the layer
    :param reference_field: name of the field to check e.g. id, fid etc.
    """
    
    # list of all values of the reference field
    all_values = layer.aggregate(aggregate=QgsAggregateCalculator.ArrayAggregate, fieldOrExpression=reference_field)[0]

    # make a dict with duplicate values and times each occurred 
    dict_with_duplicates = {value : all_values.count(value) for value in all_values if all_values.count(value) > 1 }
    
    # make a tuple of values from the dict keys
    values_to_select = tuple([*dict_with_duplicates])
    
    # selecting duplicate features by expression
    expression = f'"{reference_field}" in {values_to_select}'
    layer.selectByExpression(expression)
    
    return
    
select_features_with_duplicates(troncon_hydro, "cleabs")

# Function to save a layer in an existing gpkg
def saving_gpkg(layer, name, out_path):
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
    options.EditionCapability = QgsVectorFileWriter.CanAddNewLayer 
    options.layerName = name
    options.fileEncoding = layer.dataProvider().encoding()
    options.driverName = "GPKG"
    options.onlySelectedFeatures = True
    _writer = QgsVectorFileWriter.writeAsVectorFormat(layer, out_path, options)
    print("Update mode")
    if _writer:
            print(name, _writer)
    if _writer[0] == QgsVectorFileWriter.ErrCreateDataSource :
        print("Create mode")
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile #Create mode
        _writer= QgsVectorFileWriter.writeAsVectorFormat(layer, out_path, options)
        if _writer:
                print(name, _writer)

# save plan_d_eau_ligne
saving_gpkg(troncon_hydro, duplicate_name, referentiel_hydro_gpkg)