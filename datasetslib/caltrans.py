import os
import pandas as pd
import numpy as np
from datetime import datetime

class CalTrans():

    orig_agg_data_dic = {'dt':0,'segment':1,'district':2,'freeway':3,'travel_direction':4,'lane_type':5,
                'segment_length':6,'samples':7,'percent_observed':8,'vcount':9,'average_occupancy':10,'vspeed':11}

    orig_agg_col_names = list(orig_agg_data_dic.keys())

    #df_agg_column_names = ['dt','segment','district','freeway','direction_travel','lane_type',
    #                       'segment_length','samples','percent_observed','vcount','average_occupancy','vspeed']

    orig_agg_column_dtypes = [np.str, np.str, np.str, np.str, np.str,         np.str,
                            np.str,           np.str,   np.float32,       np.float32, np.float32, np.float32]
    df_pp_agg_column_names=['dt','freeway','direction_travel','lane_type','segment_length','samples',
                            'percent_observed','vcount','average_occupancy','vspeed']
    df_pp_agg_column_dtypes = [np.str,np.str, np.str,         np.str,    np.float32,           np.float32,
                               np.float32,       np.float32, np.float32, np.float32]

    def __init__(self):
        from . import datasets_root
        super().__init__()
        self.dataset_name='caltrans'
        self.dataset_home=os.path.join(datasets_root,self.dataset_name)


    def preprocess_agg_files(self,sourceFolder, targetFolder=None, col_names = None, date_from=None, date_to=None):

        if targetFolder is None:
            targetFolder = self.dataset_home

        if col_names is None:
            col_names = CalTrans.orig_agg_col_names

        col_idx=[CalTrans.orig_agg_col_names.index(i) for i in col_names]
        col_dtypes = dict([(CalTrans.orig_agg_col_names[i],CalTrans.orig_agg_col_dtypes[i]) for i in col_idx])

        datafiles_df = self.list_original_datafiles(sourceFolder)

#        col_names=['dt','segment','freeway','direction_travel','lane_type','segment_length','samples','percent_observed','vcount','average_occupancy','vspeed']

#        column_names = CalTrans.df_agg_column_names
#        column_dtypes = CalTrans.df_agg_column_dtypes

        #print(self.datafiles_df)
        for _,datafile in datafiles_df.iterrows():
            filename = os.path.join(sourceFolder, datafile['filename'])
            df = pd.read_csv(filename, header=None, usecols = col_idx, parse_dates=[0], infer_datetime_format=True, names = col_names, dtype = col_dtypes)

            segment_list = df['segment'].unique().tolist()

            for segment in segment_list:
                segment_df=df.loc[df['segment']==segment,df.columns != 'segment']
                dirname = os.path.join(targetFolder,
                                       datafile['agg_period'],
                                       datafile['district'],
                                       segment
                                      )
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                filename = os.path.join(dirname,'{0}_{1}_{2}.csv.gz'.format(datafile['yy'], datafile['mm'], datafile['dd']))
                segment_df.to_csv(filename,
                                  header=False,
                                  index=False,
                                  compression='gzip'
                                 )

    def list_original_datafiles(self, data_folder):
        """
        The names are in this format :
        d05_text_station_5min_2017_01_26.txt.gz
        d05_text_station_raw_2017_01_07.txt.gz
        d03_text_station_5min_2017_01_02.txt.gz

        d03 - district
        text_station - type, location
        5min, raw = 0,5,10,15 min
        yyy_mm_dd = YY,MM,DD

        :param data_folder:
        :return:
        """
        filenames = [f for f in os.listdir(data_folder) if f.endswith('.txt.gz')]

        if filenames:
            filenames_df = pd.DataFrame([x.split('_') for x in filenames],
                                        columns=['district','type','location','agg_period','yy','mm','dd']
                                        )
            # remove d from the district part
            filenames_df['district']=filenames_df['district'].str[1:]

            # remove .txt.gz from the dd part
            filenames_df['dd']=filenames_df['dd'].str[:2]
            #        filenames_df['date']= filenames_df.apply(lambda x:datetime.strptime("{0} {1} {2}".format(x['yy'], x['mm'], x['dd']), "%Y %m %d"),axis=1)
            filenames_df['date']= filenames_df.apply(lambda x:datetime.strptime('{0} {1} {2}'.format(x['yy'], x['mm'], x['dd']), '%Y %m %d'),axis=1)

            # remove 'min' from minutes
            filenames_df['agg_period']=filenames_df['agg_period'].str.extract('(\d+)',expand=False).fillna(0)

            filenames_df['filename']=filenames

        else:
            raise ValueError('No data files at {}'.format(data_folder))
        return filenames_df