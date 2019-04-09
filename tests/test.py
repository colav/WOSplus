import unittest
import warnings
import tempfile


def warn(*args, **kwargs):
    pass


warnings.warn = warn
warnings.filterwarnings("ignore")

try:
    import wosplus
except BaseException:  # (ImportError, ModuleNotFoundError):
    import sys
    sys.path.append("../wosplus")
    import wosplus

# See:
# https://jeffknupp.com/blog/2013/12/09/improve-your-python-understanding-unit-testing/

f = tempfile.NamedTemporaryFile('w', delete=False)
f.write('[FILES]\n')
f.write('Sample_WOS.xlsx = 1--LJZ4mYyQcaJ93xBdbnYj-ZzdjO2Wq2\n')
f.write('Sample_SCI.xlsx = 1-3a-hguQTk5ko8JRLCx--EKaslxGVscf\n')
f.write('Sample_SCP.xlsx = 1-IAWlMdp2U-9L2jvZUio04ub1Ym3PX-H\n')
f.close()


class PrimesTestCase(unittest.TestCase):
    """Tests for `primes.py`."""

    def setUp(self):
        self.cib = wosplus.wosplus(f.name)

        self.cib.load_biblio('Sample_WOS.xlsx')
        self.cib.load_biblio('Sample_SCI.xlsx', prefix='SCI')
        self.cib.load_biblio('Sample_SCP.xlsx', prefix='SCP')

    def test_merge(self):
        warnings.filterwarnings("ignore")
        #################################
        #Tetsing dimensions of the data #
        #################################

        # Initial data
        self.assertTrue(self.cib.WOS.shape[0] == 27)
        self.assertTrue(self.cib.SCI.shape[0] == 12)
        self.assertTrue(self.cib.SCP.shape[0] == 10)

        self.assertTrue(self.cib.WOS.shape[0] +
                        self.cib.SCI.shape[0] + self.cib.SCP.shape[0] == 49)
        # Testing after merge WOS and SCI
        self.cib.merge(left="WOS", right="SCI", left_DOI="DI", left_TI="TI", left_extra_journal="SO", left_author="AU", left_year="PY",
                       right_DOI="SCI_DI", right_TI="SCI_TI", right_extra_journal="SCI_SO", right_author="SCI_AU", right_year="SCI_PY")

        self.assertTrue(self.cib.WOS.shape[0] + self.cib.SCI.shape[0] == 39)
        self.assertTrue(self.cib.WOS_SCI.shape[0] == 29)

        # Testing after merge WOS and SCI and SCP
        self.cib.merge(left="WOS_SCI", right="SCP", left_DOI="DI", left_TI="TI", left_extra_journal="SO", left_author="AU", left_year="PY",
                       right_DOI="SCP_DOI", right_TI="SCP_Title", right_extra_journal="SCP_Source title", right_author="SCP_Authors", right_year="SCP_Year")

        self.assertTrue(
            self.cib.WOS_SCI.shape[0] + self.cib.SCP.shape[0] == 39)
        self.assertTrue(self.cib.WOS_SCI_SCP.shape[0] == 30)
        # Testing the number of items for every type combined and its combinations
        self.assertTrue(
            self.cib.WOS_SCI_SCP[self.cib.WOS_SCI_SCP.Tipo == "WOS"].shape[0] == 15)
        self.assertTrue(
            self.cib.WOS_SCI_SCP[self.cib.WOS_SCI_SCP.Tipo == "SCI"].shape[0] == 1)
        self.assertTrue(
            self.cib.WOS_SCI_SCP[self.cib.WOS_SCI_SCP.Tipo == "WOS_SCI"].shape[0] == 4)
        self.assertTrue(
            self.cib.WOS_SCI_SCP[self.cib.WOS_SCI_SCP.Tipo == "SCP"].shape[0] == 1)
        self.assertTrue(
            self.cib.WOS_SCI_SCP[self.cib.WOS_SCI_SCP.Tipo == "WOS_SCP"].shape[0] == 2)
        self.assertTrue(
            self.cib.WOS_SCI_SCP[self.cib.WOS_SCI_SCP.Tipo == "SCI_SCP"].shape[0] == 1)
        self.assertTrue(
            self.cib.WOS_SCI_SCP[self.cib.WOS_SCI_SCP.Tipo == "WOS_SCI_SCP"].shape[0] == 6)

        self.assertTrue(
            list(
                self.cib.WOS_SCI_SCP.Tipo.values) == ['WOS', 'WOS', 'WOS', 'WOS', 'WOS', 'WOS', 'WOS_SCI', 'SCI', 'WOS',
                                                      'WOS', 'WOS', 'WOS', 'WOS', 'WOS', 'WOS', 'WOS', 'WOS', 'WOS_SCI',
                                                      'WOS_SCI', 'WOS_SCI', 'WOS_SCP', 'WOS_SCI_SCP', 'WOS_SCI_SCP',
                                                      'WOS_SCI_SCP', 'SCI_SCP', 'WOS_SCP', 'WOS_SCI_SCP', 'WOS_SCI_SCP',
                                                      'WOS_SCI_SCP', 'SCP'])

    def test_normalize(self):
        self.cib.normalize()
        colname = ["DI", "TI", "SO", "PY", "SN", "AB", "EP", "AU", "PG", "BN",
                   "LA", "IS", "BP", "DE", "DT", "PM", "PU", "VL", "CT", "CY", "CL"]
        for name in colname:
            self.assertIn(name, self.cib.SCP.columns,
                          msg="Fail on SCP with %s" % name)
        colname = ["DI", "TI", "SO", "PY", "SN", "AB", "EP",
                   "AU", "LA", "IS", "BP", "DE", "DT", "PU", "VL"]
        for name in colname:  # PG and BN is not in SCI
            self.assertIn(name, self.cib.SCI.columns,
                          msg="Fail on SCI with %s" % name)


if __name__ == '__main__':
    unittest.main()
