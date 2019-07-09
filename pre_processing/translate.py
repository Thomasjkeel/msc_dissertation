## required libraries
import sys
import matplotlib.pyplot as plt # v3.0.3
import geopandas as gpd # v0.4.0+26.g9e584cc

## translations
purpose_translations = {"None":"None",'Reconduire / aller chercher une personne':'pick_up_a_person',
       "Travail / Rendez-vous d'affaires":'work', 'Magasinage / emplettes':'shops',
       'Retourner à mon domicile':'returning_home', 'Santé':'health', 'Loisir':'leisure', 'Éducation':'education',
       'Autre':'other', 'Repas / collation / café':'cafe', 'ND':'not_available'}

mode_translations = {"Voiture / Moto":"car", "À pied":"walking", "Transport collectif":"public_transport",
                     "Autopartage":"car_sharing", "Vélo":"cycling", "Taxi":"taxi",
                     "Autre":"other", "ND":"not_available"}
    
def read_file(filename):
    ## read in file from http://donnees.ville.montreal.qc.ca/dataset/mtl-trajet
    gdf = gpd.read_file(filename, encoding='utf-8') # utf-8 needed to read french letters
    return gdf

def mode_to_new_name(mode_names):
    
    if mode_names:
        mode_list = mode_names.split(',')
        translations = []
        for mode in mode_list:
            translations.append(mode_translations[mode.lstrip()])
        return str(translations).strip('[]').replace("'", '')
    else:
        return mode_names
    
def make_translations(gdf):
    ## make translations
    gdf['purpose'] = gd['purpose'].apply(lambda pur: purpose_translations[pur] if pur else pur)
    gdf['mode'] = gdf['mode'].apply(mode_to_new_name)
    return gdf

def main():
    filename = str(sys.argv[1])
    print(filename)
    try:
        gdf = read_file(filename)
    except:
        "print please enter path to MTL Trajet data e.g. data/mtl_traject.shp"
    print("making translations")
    gdf = make_translations(gdf)
    print("saving file in same location")
    gdf.to_file(filename, encoding='utf-8')

if __name__ == "__main__":
    main()
    