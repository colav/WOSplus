try:
    import wosplus
except BaseException:  # (ImportError, ModuleNotFoundError):
    import sys
    sys.path.append("../wosplus")
    import wosplus

import unittest
import warnings
import tempfile

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

    def test_merge(self):
        warnings.filterwarnings("ignore")
        cib = wosplus.wosplus(f.name)

        cib.load_biblio('Sample_WOS.xlsx')
        cib.load_biblio('Sample_SCI.xlsx', prefix='SCI')
        cib.load_biblio('Sample_SCP.xlsx', prefix='SCP')

        self.assertTrue(cib.WOS.shape[0] +
                        cib.SCI.shape[0] + cib.SCP.shape[0] == 48)

        cib._merge(left="WOS", right="SCI", left_DOI="DI", left_TI="TI", left_extra_journal="SO", left_author="AU", left_year="PY",
                   right_DOI="SCI_DI", right_TI="SCI_TI", right_extra_journal="SCI_SO", right_author="SCI_AU", right_year="SCI_PY")

        self.assertTrue(cib.WOS.shape[0] + cib.SCI.shape[0] == 38)
        self.assertTrue(cib.WOS_SCI.shape[0] == 28)

        cib._merge(left="WOS_SCI", right="SCP", left_DOI="DI", left_TI="TI", left_extra_journal="SO", left_author="AU", left_year="PY",
                   right_DOI="SCP_DOI", right_TI="SCP_Title", right_extra_journal="SCP_Source title", right_author="SCP_Authors", right_year="SCP_Year")

        self.assertTrue(cib.WOS_SCI.shape[0] + cib.SCP.shape[0] == 38)
        self.assertTrue(cib.WOS_SCI_SCP.shape[0] == 30)

        cib._merge(left="WOS", right="SCP", left_DOI="DI", left_TI="TI", left_extra_journal="SO", left_author="AU", left_year="PY",
                   right_DOI="SCP_DOI", right_TI="SCP_Title", right_extra_journal="SCP_Source title", right_author="SCP_Authors", right_year="SCP_Year")

        cib._merge(left="SCI", right="SCP", left_DOI="SCI_DI", left_TI="SCI_TI", left_extra_journal="SCI_SO", left_author="SCI_AU", left_year="SCP_PY",
                   right_DOI="SCP_DOI", right_TI="SCP_Title", right_extra_journal="SCP_Source title", right_author="SCP_Authors", right_year="SCP_Year")

        cib.merge()
        # NOTE: added tests for more merge configs

        self.assertTrue(
            list(
                cib.WOS_SCI_SCP.Tipo.values) == [
                'WOS',
                'WOS',
                'WOS',
                'WOS',
                'WOS',
                'WOS',
                'WOS_SCI',
                'SCI',
                'WOS',
                'WOS',
                'WOS',
                'WOS',
                'WOS',
                'WOS',
                'WOS',
                'WOS',
                'WOS',
                'WOS_SCI',
                'WOS_SCI',
                'WOS_SCI',
                'WOS_SCP',
                'WOS_SCI_SCP',
                'WOS_SCI_SCP',
                'WOS_SCI_SCP',
                'WOS_SCP',
                'WOS_SCI_SCP',
                'WOS_SCI_SCP',
                'WOS_SCI_SCP',
                'SCP',
                'SCP'])


if __name__ == '__main__':
    unittest.main()
