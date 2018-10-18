import requests
import io
'''
Based on:
http://stackoverflow.com/a/39225272

Auxilary functions for Pandas DaraFrame extended method:
read_drive_excel(...) in wosplus class
WARNING: Only  Google Drive id's are used here! Not file names.
'''

def pandas_from_google_drive_csv(id,gss_sheet=0,gss_query=None):
    '''
    Read Google spread sheet by id.
    Options:
       gss_sheet=N : if in old format select the N-sheet
       gss_query=SQL_command: Filter with some SQL command
       example 
         SQL_command: 'select B,D,E,F,I where (H contains 'GFIF') order by D desc'
    '''
    import pandas as pd
    if not gss_query:
        url='https://docs.google.com/spreadsheets/d/%s/gviz/tq?tqx=out:csv&gid=%s' %(id,gss_sheet)
    else:
        url='https://docs.google.com/spreadsheets/d/%s/gviz/tq?tqx=out:csv&gid=%s&tq=%s' %(id,gss_sheet,gss_query)
    r=requests.get(url)
    if r.status_code==200:
        csv_file=io.StringIO(r.text) # or directly  with: urllib.request.urlopen(url)
        return pd.read_csv( csv_file,keep_default_na=False)
    
def save_response_content(response, file=None):
    '''
    See help from 
    download_public_drive_file(...)
    '''
    CHUNK_SIZE = 32768
    if file:
        with open(file, 'wb') as f:
            f.write(response.content)
        return
    else:
        chunks=b''
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                    chunks=chunks+chunk

        try: 
            ior=io.StringIO(chunks.decode())#.read()
        except  UnicodeDecodeError:
            ior=io.BytesIO(chunks)

        # returns the file object
        return ior
    
def download_public_drive_file(file=None,id='1snzdsa-RLwYIf8MUffauaD2ZjNr1U2Os'):
    '''
    Download file from Google Drive public id
    If 
      file=None
    returns: 
      * File object for a binary file
        Example: 
          import pandas as pd
          pd.read_excel(  download_public_drive_file(id='0BxoOXsn2EUNIMldPUFlwNkdLOTQ')  )[:1]
          
      * String for a txt file
        Example:
          print( download_public_drive_file(id='1snzdsa-RLwYIf8MUffauaD2ZjNr1U2Os').read()[:200] )
    '''
    response=requests.get('https://docs.google.com/uc?export=download&id='+id)
    return save_response_content(response, file=file)

def download_file_from_google_drive(gid,destination=None,binary=True):
    '''
    Download file from google drive as binary (default) or txt file.
    If not destination the file object is returned
    Example: Let id="XXX" a txt file:
    1) fb=download_file_from_google_drive("XXX") ; fb.decode() #to convert to text file
    2) ft=download_file_from_google_drive("XXX",binary=False) # txt file
    3) fb=download_file_from_google_drive("XXX",'output_file') # always binay
    '''
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : gid }, stream = True)
    token = get_confirm_token(response)
    
    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)
    
    # Deprecated: binary
    return save_response_content(response, file=destination)


def download_file_from_local_drive(localfile,destination=None,binary=True):
    '''
    Download file from google drive as binary (default) or txt file.
    If not destination the file object is returned
    Example: Let id="XXX" a txt file:
    1) fb=download_file_from_google_drive("XXX") ; fb.decode() #to convert to text file
    2) ft=download_file_from_google_drive("XXX",binary=False) # txt file
    3) fb=download_file_from_google_drive("XXX",'output_file') # always binay
    '''
    URL = "file://"

    session = requests.Session()
    
    session.mount('file://', LocalFileAdapter())
    
    r=requests_session.get('file://./Sample_WOS.txt')

    response = session.get(URL+'./'+localfile)
    token = get_confirm_token(response)
    
    #DEPRECATED: binary
    return save_response_content(response, file=destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def old_save_response_content(response, destination=None,binary=True):
    CHUNK_SIZE = 32768

    if destination:
        f=open(destination, "wb") #binary file
    else:
        chunks=b''
    for chunk in response.iter_content(CHUNK_SIZE):
        if chunk: # filter out keep-alive new chunks
            if destination:
                f.write(chunk)
            else:
                chunks=chunks+chunk
    if destination:
        f.close()  #writes the file
    else:
        if binary:
            return io.BytesIO(chunks) # returns the file object
        else:
            return io.StringIO(chunks.decode()) # returns the file object    

def query_drive_csv(
    gss_url="https://spreadsheets.google.com",
    gss_format="csv",
    gss_key="0AuLa_xuSIEvxdERYSGVQWDBTX1NCN19QMXVpb0lhWXc",
    gss_sheet=0,
    gss_query="select B,D,E,F,I where (H contains 'GFIF') order by D desc",
    gss_keep_default_na=False
    ):
    import pandas as pd
    issn_url="%s/tq?tqx=out:%s&tq=%s&key=%s&gid=%s" %(gss_url,\
                                           gss_format,\
                                           gss_query,\
                                           gss_key,\
                                           str(gss_sheet))

    return pd.read_csv( issn_url.replace(' ','+') )
