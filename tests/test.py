try:
    import wosplus
except: #(ImportError, ModuleNotFoundError):
    import sys
    sys.path.append("../wosplus")
    import wosplus
    
import unittest
import warnings
import tempfile
'''
See: https://jeffknupp.com/blog/2013/12/09/improve-your-python-understanding-unit-testing/
'''
f=tempfile.NamedTemporaryFile('w',delete=False)
f.write('[FILES]\n')
f.write('Sample_WOS.xlsx = 1--LJZ4mYyQcaJ93xBdbnYj-ZzdjO2Wq2\n')
f.write('Sample_SCI.xlsx = 1-3a-hguQTk5ko8JRLCx--EKaslxGVscf\n')
f.write('Sample_SCP.xlsx = 1-IAWlMdp2U-9L2jvZUio04ub1Ym3PX-H\n')
f.close()

class PrimesTestCase(unittest.TestCase):
    """Tests for `primes.py`."""
    def test_merge(self):
        warnings.filterwarnings("ignore")
        cib=wosplus.wosplus(f.name)
     
        cib.load_biblio('Sample_WOS.xlsx')
        cib.load_biblio('Sample_SCI.xlsx',prefix='SCI')
        cib.load_biblio('Sample_SCP.xlsx',prefix='SCP')

        self.assertTrue( cib.WOS.shape[0]+cib.SCI.shape[0]+cib.SCP.shape[0] == 48 )
         
        cib.merge(left='WOS',right='SCI')
         
        self.assertTrue ( cib.WOS.shape[0]+cib.SCI.shape[0] == 38  )
        self.assertTrue (  cib.WOS_SCI.shape[0] == 28 )
        
        cib.merge(left='WOS_SCI',right='SCP')
         
        self.assertTrue( cib.WOS_SCI.shape[0]+cib.SCP.shape[0] == 38  )
        self.assertTrue( cib.WOS_SCI_SCP.shape[0] == 30  )

        self.assertTrue(list( cib.WOS_SCI_SCP.Tipo.values )==['WOS','WOS',
           'WOS','WOS','WOS','WOS','WOS_SCI','SCI','WOS','WOS','WOS','WOS',
           'WOS','WOS','WOS','WOS','WOS','WOS_SCI','WOS_SCI','WOS_SCI',
           'WOS_SCP','WOS_SCI_SCP','WOS_SCI_SCP','WOS_SCI_SCP','WOS_SCP',
           'WOS_SCI_SCP','WOS_SCI_SCP','WOS_SCI_SCP','SCP','SCP'])

if __name__ == '__main__':
    unittest.main()


