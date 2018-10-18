#!/usr/bin/env python3
import re
import pandas as pd
from configparser import ConfigParser
try:
    from ._google_drive_tools import *
    from ._pajek_tools import *
    from ._wos_scp import *
    from ._merge_tools import *
    from ._wos_parser import *
except (SystemError, ImportError):
    from _google_drive_tools import *
    from _pajek_tools import *
    from _wos_scp import *
    from _merge_tools import *
    from _wos_parser import *

#TODO: change Tipo for Type or something similar
#pd.set_option('display.max_rows', 500)
#pd.set_option('display.max_columns', 500)
#pd.set_option('display.max_colwidth',1000)
def grep(pattern,multilinestring):
    '''Grep replacement in python
    as in: $ echo $multilinestring | grep pattern
    dev: re.M is for multiline strings
    '''
    grp=re.finditer('(.*)%s(.*)' %pattern, multilinestring,re.M)
    return '\n'.join([g.group(0) for g in grp])

def merge_inner_interior_exterior(LEFT,RIGHT,on_condition='SCP_DOI',left_on='ST',right_on='Simple_Title',\
            left_series=pd.Series(),right_series=pd.Series(),\
            left_extra_on='SO',right_extra_on='UDEA_nombre revista o premio',\
            close_matches=False,cutoff=0.6,cutoff_extra=0.6):
    '''
    Given a df LEFT and a RIGHT[RIGHT[on_condition]!=''] fully True, then
    Get a tuple with the following 3 dataframes
    1) left-right intersection (inner): LR
    1) pure left (interior): L-LR
    3) pure right: R-LR (exterior)
    '''
    if LEFT.shape[0]==0:
        print('All entries matched',r,l)
        return pd.DataFrame(),pd.DataFrame(),RIGHT
    
    RIGHT=RIGHT[RIGHT[on_condition]!='']
    if RIGHT.shape[0]:
        interior,inner,exterior=merge_by_series(LEFT.copy(),RIGHT.copy(),left_on=left_on,right_on=right_on,\
                                   left_series=left_series,right_series=right_series,\
                                   left_extra_on=left_extra_on,right_extra_on=right_extra_on,\
                                   close_matches=close_matches,cutoff=cutoff,cutoff_extra=cutoff_extra)
        if LEFT.shape[0]>=interior.shape[0] and RIGHT.shape[0]>=exterior.shape[0]:
            return inner.reset_index(drop=True),interior.reset_index(drop=True),exterior.reset_index(drop=True)
    else:
        return (pd.DataFrame(),pd.DataFrame(),pd.DataFrame())


#Start here
class wosplus:
    """
    Input files assumed to have public links in Google Drive
    A config file, e.g 'drive.cfg' is expected with the following structure
    ==============================================================
    [FILES]
    WOS_FILE.xlsx              = 1--LJZ4mYyQcaJ93xBdbnYj-ZzdjO2Wq2
    ...
    ==============================================================
    USAGE:
        import wosplus as wp
        WOS=wp.wosplus('drive.cfg')
        #check Google Drive id for file
        WOS.drive_file.get('WOS_FILE.xlsx')
        #load biblio
        WOS.load_biblio('WOS_FILE.xlsx')
        # DataFrame in WOS.WOS or WOS.biblio['WOS']
  
    The main method is 'load_biblio' it must have a prefix according to
    the type of supported bibliography. This prefix will be appended
    to the ALL the columns of the generated bibligraphy

    wp.type gives the type of bibliography Data Base.
    Currently implenented:
      * WOS: two characters columns
      * SCI: prefixed SCI_ columns is returned
      * SCP: prefixed SCP_ columns is returned 
    and any combinantion
    of them keeping the same ordering.

    The type mus be declared with the 'load_biblio' with the 'prefix' option
    (Default type is WOS)
    """

    def __init__(self,cfg_file=''):
        self.df=pd.DataFrame()
        '''
        Based on:
        http://stackoverflow.com/a/39225272
        '''
        cfg=ConfigParser()
        cfg.optionxform=str
        if cfg_file:
            tmp=cfg.read(cfg_file)
        else:
            tmp=cfg.read_dict({'FILES':
                    {'Sample_WOS.xlsx':'0BxoOXsn2EUNIMldPUFlwNkdLOTQ'}})
            
        self.drive_file=cfg['FILES']
        self.type=pd.Series()
        self.biblio=pd.Series()

    def read_drive_excel(self,file_name,**kwargs):
        '''
        TODO: Make independent of the class!
        Generalization of the Pandas DataFrame read_excel method
        to include google drive file names:
         
         Read excel or csv file from google drive
         Requires a self.drive_file dictionary intialized with the class
         (see below) with the id's for the
         google drive file names.
         If the file_name is not found in the drive_file dictionary it is read locally.
         If the file_name have an extension .csv, try to read the google spreadsheet
         directly: check pandas_from_google_drive_csv for passed options
         WARNING: ONLY OLD Google Spread Sheet allows to load sheet different from 0

         drive_file dictionary: for some file, e.g 'drive.cfg' the format must be:
          $ cat drive.cfg
          [FILES]
          Sample_WOS.xlsx = 0BxoOXsn2EUNIMldPUFlwNkdLOTQ
        '''
        # Try to load Google spreadsheet if extension is csv
        if re.search('\.csv$',file_name):
            if self.drive_file.get(file_name):
                return pandas_from_google_drive_csv(
                    self.drive_file.get(file_name),**kwargs)
            else:
                return pd.read_csv(file_name,**kwargs)
       
        # Try to load xlsx file if file extension is not csv
        if self.drive_file.get(file_name):
            return pd.read_excel( download_file_from_google_drive(
                self.drive_file.get(file_name) ) ,**kwargs)  # ,{} is an accepted option
        else:
            return pd.read_excel(file_name,**kwargs)
    def load_biblio(self,WOS_file,prefix='WOS'):
        """
        Load WOS xlsx file, or if prefix is given:
          prefix='SCI': Load SCI xlsx file and append the 'SCI_' prefix in each column
          prefix='SCP': Load SCI csv file and append the 'SCP_' prefix in each column
        and add the WOS, SCI, or SCP  attribute to self.
        """
        from pathlib import Path
        import sys
        DOI='DI'
        if prefix=='SCP': #Only if pure scopus
            DOI='DOI'
        #elif: #Other no WOS-like pures

        if not re.search('\.txt$',WOS_file):
            WOS=self.read_drive_excel(WOS_file)
        else:
            id_google_drive=self.drive_file.get('{}'.format(WOS_file))
            if id_google_drive:                                     
                wos_txt=download_file_from_google_drive(  id_google_drive )#,binary=False)
                WOS=wos_to_list_to_pandas(wos_txt)
            else: #check local file
                my_file = Path(WOS_file)
                if my_file.is_file():
                    WOS=wos_parser(WOS_file)
                else:
                    sys.exit('WOS File: {}, NOT FOUND!'.format(WOS_file))

        WOS=fill_NaN(WOS)
        if prefix=='SCI':
            exec('self.{}_not_prefix=WOS'.format(prefix))
        
        
        if 'DI' in WOS and 'TI' in WOS and 'SO' in WOS:
            WOS['DI']=WOS['DI'].str.strip()
            WOS['TI']=WOS['TI'].str.strip().str.replace('\n',' ')
            WOS['SO']=WOS['SO'].str.strip()
        if 'X1' in WOS:
            WOS_ti,WOS_not_ti=df_split(WOS,on='TI',on_not_condition=True)
            WOS_not_ti['TI']=WOS_not_ti['X1']
            WOS=WOS_ti.append(WOS_not_ti).reset_index(drop=True)
        
        if 'TI' in WOS:
            WOS=WOS.drop_duplicates('TI')

        #Drop duplicated DOIS
        if DOI in WOS:
            WOS_di,WOS_not_di=df_split(WOS,on=DOI,on_not_condition=True)
            WOS=WOS_not_di.append(WOS_di.drop_duplicates(DOI)).reset_index(drop=True)

            
        if prefix != 'WOS' and not re.search('_',prefix):
            #check if already present
            WOS=columns_add_prefix(WOS,prefix)

        # Without prefix columns
        if not WOS.get('Tipo') and not re.search('_',prefix):
            WOS['Tipo']=prefix
        else:
            print('WARNING: Biblio already has a "Tipo" column')
            
        exec('self.{}=WOS'.format(prefix))
        self.type['{}'.format(prefix)]='{}'.format(prefix)
        self.biblio['{}'.format(prefix)]=WOS
        
    def merge(self,left='WOS',right='SCI',
                   right_DOI=None,right_TI=None,right_extra_journal=None,
                   right_author=None,right_year=None,
              DEBUG=False):
        """
        Merge left and right bibliographic dataframes by TYPE and with 
        Python merge ooption: `how='outer'`.
        
        The TYPE must coincide with the Object attribute Dataframe: eg:
        `left='WOS'` imply that WOS must be an attribute of
        self: self.WOS
        `right='SCI'` imply that WOS must be an attribute of
        self: self.WOS
        The DataFrame attributtes of the object `self` are populated by using
          `self.loadbiblio(file)`: See `self` help for further instructions.

        The self.right DataFrame need to have some mandatories columns:
         [[right_DOI,right_TI,right_extra_journal,right_author,right_year]]
         They are automatically defined for self.righ TYPE: SCI and SCP and
         must be given for other TYPE
        
        Output:
        The resulting DataFrame is returned as:
          * self.left_right # with strings names converted into variable names
          * self.bibilio['left_right'] # pd.Series
        and also the new resulting TYPE is stored as
          * self.Tipo['left_right'] -> 'left_right' # pd.Series
          
        The merged DOI, Titles and Journal Names are stored in
        the WOS like `self.left_right` columns: DI,TI,SO with `self.left`
        priority for the values.
        """
        if not hasattr(self,left) or not hasattr(self,right):
            sys.exit('ERROR:  {} and {} must be attributes of class {}'.format(left,right,self.__class__.__name__))
            
        if left not in self.biblio or right not in self.biblio:
            sys.exit('ERROR: missing biblio Series in {}'.format(left,right,self.__class__.__name__)  )

        if left not in self.type or right not in self.type:
            sys.exit('ERROR: missing type Series in {}'.format(left,right,self.__class__.__name__)  )
            
        left_df=self.biblio[left].copy()
        right_df=self.biblio[right].copy()
        if DEBUG:
            print('intial: {}'.format(left_df.shape[0]+right_df.shape[0]))
        if left=='WOS' or  re.search('^WOS_',left):
            left_DOI='DI'
            left_TI='TI'
            left_extra_journal='SO' #helps with similiraty search  by Title
        #elif
        #else:
            #sys.error('not supported left type')
        #clean Tipo
        if 'Tipo' in right_df:
            right_df=right_df.drop('Tipo',axis='columns')
            
        if right=='SCI':
            right_DOI='SCI_DI'
            right_TI='SCI_TI'
            right_extra_journal='SCI_SO' #helps with similiraty search  by Title
            right_author='SCI_AU'
            right_year='SCI_PY'
        elif right=='SCP':
            if 'SCP_Title' in right_df and not 'SCP_Title_0' in right_df:
                right_df=split_translated_columns(right_df.copy(),on='SCP_Title',sep='\[',min_title=16)
            right_DOI='SCP_DOI'
            right_TI='SCP_Title'
            right_extra_journal='SCP_Source title' #helps with similiraty search  by Title
            right_author='SCP_Authors'
            right_year='SCP_Year'

        #else:
            #sys.error('not supported right type')

        # Merge on DOIs                                 
            
        LEFT_RIGHT_inner=pd.DataFrame() 
        RIGHT_on=right_DOI
        # RIGHT: no empty values for column 'right_df'
        RIGHT,next_RIGHT=df_split(right_df,on=RIGHT_on,on_not_condition=True)
        #full_RIGHT=RIGHT.append(next_RIGHT)
        LEFT=left_df
        LEFT_on=left_DOI
        LEFT_series=clean(LEFT[LEFT_on])
        RIGHT_series=clean(RIGHT[RIGHT_on])

        LR=merge_inner_interior_exterior(LEFT.copy(),RIGHT.copy(),\
                    on_condition=RIGHT_on,left_on='LEFT_simple_doi',right_on='RIGHT_simple_doi',\
                                   left_series=LEFT_series,right_series=RIGHT_series)
        if LR[0].shape[0]:
            inner,new_LEFT,new_RIGHT=LR # LEFT.shape[0]=inner.shape[0]+new_LEFT.shape[0]
                                        # RIGHT.shape[0]=inner.shape[0]+new_RIGHT.shape[0]
            inner['Tipo']=inner['Tipo']+'_{}'.format(right)        
            LEFT_RIGHT_inner=LEFT_RIGHT_inner.append(inner).reset_index(drop=True)
        else:
            new_LEFT=LEFT; new_RIGHT= RIGHT
            

        if DEBUG:
            print(inner.shape[0],new_LEFT.shape[0],new_RIGHT.shape[0],'=,...,=')
            print(LEFT.shape,RIGHT.shape)
            print(new_LEFT.shape,(next_RIGHT.append(new_RIGHT)).shape,LEFT_RIGHT_inner.shape)
            print( ( ( new_LEFT.append(LEFT_RIGHT_inner)  ).append(new_RIGHT) ).append(next_RIGHT).shape )
            
        #Merge on (splitted) Titles: generated with 'split_translated_columns' before
        #next_RIGHT have column information even if empty
        for nTI in [right_TI]+[ x for x in next_RIGHT.columns
                                if re.search( '{}_[0-9]+'.format(right_TI),x  )]:
            RIGHT_on=nTI
            full_RIGHT=new_RIGHT.append(next_RIGHT)
            RIGHT,next_RIGHT=df_split(full_RIGHT,on=RIGHT_on,on_not_condition=True)
            RIGHT=RIGHT.drop_duplicates(RIGHT_on)
            RIGHT_series=clean(RIGHT[RIGHT_on])

            LEFT=new_LEFT
            LEFT_series=clean(LEFT[left_TI])

            LR=merge_inner_interior_exterior(LEFT.copy(),RIGHT.copy(),\
                                on_condition=RIGHT_on,left_on='LEFT_Simple_title',right_on='RIGHT_Simple_title',\
                                  left_series=LEFT_series,right_series=RIGHT_series)
            if LR[0].shape[0]:
                inner,new_LEFT,new_RIGHT=LR
                inner['Tipo']=inner['Tipo']+'_{}'.format(right)
                LEFT_RIGHT_inner=LEFT_RIGHT_inner.append(inner).reset_index(drop=True)
            else:
                new_LEFT=LEFT; new_RIGHT= RIGHT

                
            if DEBUG:
                print(inner.shape[0],new_LEFT.shape[0],new_RIGHT.shape[0])
                print(LEFT.shape,RIGHT.shape)
                print(new_LEFT.shape,(next_RIGHT.append(new_RIGHT)).shape,LEFT_RIGHT_inner.shape) 
                print( ( ( new_LEFT.append(LEFT_RIGHT_inner)  ).append(new_RIGHT) ).append(next_RIGHT).shape )
        
        # Merge on Similar Titles
        for nTI in [right_TI]+[ x for x in next_RIGHT.columns 
                                if re.search( '{}_[0-9]+'.format(right_TI),x  )]:                
            RIGHT_on=nTI
            full_RIGHT=new_RIGHT.append(next_RIGHT)
            RIGHT,next_RIGHT=df_split(full_RIGHT,on=RIGHT_on,on_not_condition=True)
            RIGHT=RIGHT.drop_duplicates(RIGHT_on)
            RIGHT_series=clean(RIGHT[RIGHT_on]).str.replace('\[','').str.replace('\]','')

            LEFT=new_LEFT
            LEFT_series=clean(LEFT[left_TI])

            LR=merge_inner_interior_exterior(LEFT.copy(),RIGHT.copy(),\
                                on_condition=RIGHT_on,left_on='LEFT_Simple_title',right_on='RIGHT_Simple_title',\
                                  left_series=LEFT_series,right_series=RIGHT_series,\
                                  left_extra_on=left_extra_journal,right_extra_on=right_extra_journal,\
                                  close_matches=True,cutoff=0.6)
            if LR[0].shape[0]:
                inner,new_LEFT,new_RIGHT=LR
                inner['Tipo']=inner['Tipo']+'_{}'.format(right)
                LEFT_RIGHT_inner=LEFT_RIGHT_inner.append(inner).reset_index(drop=True)
            else:
                new_LEFT=LEFT; new_RIGHT= RIGHT


            if DEBUG:
                print(inner.shape[0],new_LEFT.shape[0],new_RIGHT.shape[0])
                print(LEFT.shape,RIGHT.shape)
                print(new_LEFT.shape,(next_RIGHT.append(new_RIGHT)).shape,LEFT_RIGHT_inner.shape) 
                print( ( ( new_LEFT.append(LEFT_RIGHT_inner)  ).append(new_RIGHT) ).append(next_RIGHT).shape )
                
        
        
        full_RIGHT=next_RIGHT.append(new_RIGHT)
        full_RIGHT['Tipo']=right
        full_RIGHT['DI']=full_RIGHT[right_DOI]
        full_RIGHT['TI']=full_RIGHT[right_TI]
        full_RIGHT['SO']=full_RIGHT[right_extra_journal]
        full_RIGHT['AU']=full_RIGHT[right_author]
        full_RIGHT['PY']=full_RIGHT[right_year]

        LEFT_RIGHT=new_LEFT
        LEFT_RIGHT=LEFT_RIGHT.append(LEFT_RIGHT_inner)
        LEFT_RIGHT=LEFT_RIGHT.append(full_RIGHT)
        LEFT_RIGHT=fill_NaN(LEFT_RIGHT).reset_index(drop=True)
         
        if DEBUG:    
            self.LEFT=LEFT
            self.RIGHT=RIGHT
            self.new_LEFT=new_LEFT
            self.new_RIGHT=new_RIGHT
            self.LEFT_RIGHT_inner=LEFT_RIGHT_inner
            self.full_RIGHT=full_RIGHT
        
        exec('self.{}_{}=LEFT_RIGHT'.format(left,right))
        self.type['{}_{}'.format(left,right)]='{}_{}'.format(left,right)
        self.biblio['{}_{}'.format(left,right)]=LEFT_RIGHT

if __name__=='__main__':
    WOS_file='CIB_Wos.xlsx'
    SCI_file='CIB_Scielo.xlsx'
    SCP_file='CIB_Scopus.csv'
    cib=wosplus('drive.cfg')
    cib.load_biblio(WOS_file)
