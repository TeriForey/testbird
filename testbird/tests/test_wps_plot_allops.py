import pytest

from pywps import Service
from pywps.tests import assert_response_success

from testbird.tests.common import client_for
from testbird.processes.wps_plot_allops import PlotAll


@pytest.mark.online
def test_wps_plot_allops():
    client = client_for(Service(processes=[PlotAll()]))
    datainputs = "filelocation={}".format(
        "/home/t/trf5/birdhouse/testoutputs/BCK_3-hourly_CAPEVERDE/Outputs",
    )
    resp = client.get(
        service='wps', request='execute', version='1.0.0',
        identifier='plotall',
        datainputs=datainputs)
    assert_response_success(resp)