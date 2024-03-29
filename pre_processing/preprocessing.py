# required libraries
import sys
import geopandas as gpd # v0.4.0+26.g9e584cc
import pandas as pd

# translations
purpose_translations = {"None":"None",'Reconduire / aller chercher une personne':'pick_up_a_person',
       "Travail / Rendez-vous d'affaires":'work', 'Magasinage / emplettes':'shops',
       'Retourner à mon domicile':'returning_home', 'Santé':'health', 'Loisir':'leisure', 'Éducation':'education',
       'Autre':'other', 'Repas / collation / café':'cafe', 'ND':'not_available'}

mode_translations = {"Voiture / Moto":"car", "À pied":"walking", "Transport collectif":"public_transport",
                     "Autopartage":"car_sharing", "Vélo":"cycling", "Taxi":"taxi",
                     "Autre":"other", "ND":"not_available"}

CAN_LAM = {'init': 'epsg:3347'} ## convert to Canada Lambert Projection (https://epsg.io/3347)


class dataPreProcessing:
    """
    group of functions for the data preprocessing phase

    Parameters
    ----------
    filename : string
        path to file containing the MTL-Trajet data
    """
    def __init__(self, filename):
        self.filename = filename

    @classmethod
    def translate_data(cls, filename):
        data = cls(filename)
        data.read_file()
        data.make_translations()
        return data

    def read_file(self):
        """
        reads in the file containing MTL-Trajet data from http://donnees.ville.montreal.qc.ca/dataset/mtl-trajet
        :return:
            self : dataPreProcessing Object containing .data which is a geopandas.GeoDataFrame
        """

        try:
            self.data = gpd.read_file(self.filename, encoding='utf-8')  # utf-8 needed to read french letters
        except:
            print("path/to/filename not found")
        return self

    @staticmethod
    def mode_to_new_name(mode_names):
        """
        translates a string, potentially containing a list, into english using the global translation dictionaries
        found at the head of the file

        :param:
            mode_names : string
            transport mode names
        :return:
            mode_names : string
        """
        if mode_names:
            mode_list = mode_names.split(',')
            translations = []
            for mode in mode_list:
                translations.append(mode_translations[mode.lstrip()])
            return str(translations).strip('[]').replace("'", '')
        else:
            return mode_names

    def make_translations(self):
        """
        translates the columns and fields of the data from French to English
        """
        if 'ND' in self.data['purpose'].unique():
            self.data['purpose'] = self.data['purpose'].apply(lambda pur: purpose_translations[pur] if pur else pur)
        if 'ND' in self.data['mode'].unique():
            self.data['mode'] = self.data['mode'].apply(self.mode_to_new_name)
        return self

    def change_projection(self):
        """
        Changes the projection of the data to EPSG:3347
        """
        # convert to Canada Lambert Projection (https://epsg.io/3347)
        if self.data.crs != CAN_LAM:
            print("translating data")
            self.data = self.data.to_crs(crs=CAN_LAM)
        else:
            print("correct crs")
        return self

    def calc_journeytime(self):
        """
        Calculate the time of each journey in the data
        """
        self.data['journeytime'] = pd.to_datetime(self.data['endtime']) - pd.to_datetime(self.data['starttime'])
        self.data['journeytime'] = self.data['journeytime'].apply(lambda tm: tm.seconds)
        return self

    def calc_distance(self):
        """
        Calculate the distance of each journey in the data
        """
        if self.data.crs != CAN_LAM:
            print("please convert the projection using '.change_projection' first")
        else:
            if 'distance_m' not in self.data.columns:
                print("calculating distance")
                self.data['distance_m'] = self.data['geometry'].apply(lambda row: row.length)
            else:
                print('distance already calculated')
        return self

# def main():
#     filename = str(sys.argv[1])
#     print(filename)
#     try:
#         gdf = read_file(filename)
#     except:
#         "print please enter path to MTL Trajet data e.g. data/mtl_traject.shp"
#     print("making translations")
#     gdf = make_translations(gdf)
#     print("saving file in same location")
#     gdf.to_file(filename, encoding='utf-8')

# if __name__ == "__main__":
#     main()
