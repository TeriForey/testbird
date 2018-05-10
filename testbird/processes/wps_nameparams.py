from pywps import Process
from pywps import ComplexOutput, Format
from pywps import LiteralInput, LiteralOutput, BoundingBoxInput
from pywps.exceptions import InvalidParameterValue
from pywps.app.Common import Metadata

from testbird.run_name import run_name


import logging
LOGGER = logging.getLogger("PYWPS")


class RunNAME(Process):
    """
    Notes
    -----

    This will take and regurgitate all the parameters required to run NAME.
    It should make it easier to then add in the actual process.
    """
    def __init__(self):
        inputs = [
            LiteralInput('title', 'Title of run', data_type='string',
                         abstract="Title of run"),
            LiteralInput('longitude', 'Longitude', data_type='float',
                         abstract="Location of release",
                         default=-24.867222),
            LiteralInput('latitude', 'Latitude', data_type='float',
                         abstract="Location of release",
                         default=16.863611),
            BoundingBoxInput('domain', 'Domain coordinates', crss=['epsg:4326'],
                         abstract='Coordinates to search within',
                         min_occurs=1),
            LiteralInput('elevation','Elevation', data_type='integer',
                         abstract = "release elevation, m agl for land, m asl for marine release",
                         default=10, min_occurs=0),
            LiteralInput('elevation_range_min','Elevation Range Min', data_type='integer',
                         abstract="Minimum range of elevation",
                         default=None, min_occurs=0),
            LiteralInput('elevation_range_max', 'Elevation Range Max', data_type='integer',
                         abstract = "Maximum range of elevation",
                         default=None, min_occurs=0),

            LiteralInput('runBackwards', 'Run Backwards', data_type='boolean',
                         abstract = 'Whether to run backwards in time (default) or forwards',
                         default = '1', min_occurs=0),
            LiteralInput('time', 'Time to run model over', data_type='integer',
                         abstract = 'Time',
                         default=1),
            LiteralInput('timeFmt','Time format', data_type='string',
                         abstract='choose whether to measure time in hours or days',
                         allowed_values = ['days','hours'], default='days'),
            LiteralInput('elevationOut', 'Elevation averaging ranges', data_type='string',
                         abstract='Elevation range where the particle number is counted (m agl)'
                                  " Example: 0-100",
                         default='0-100', min_occurs=1, max_occurs=4),
            LiteralInput('resolution','Resolution', data_type='float',
                         abstract='degrees, note the UM global Met data was only 17Km resolution',
                         allowed_values=[0.05,0.25], default=0.25, min_occurs=0),
            LiteralInput('timestamp','timestamp of runs', data_type='string',
                         abstract='how often the prog will run?',
                         allowed_values=['3-hourly','daily']),
            LiteralInput('dailytime','daily run time', data_type='time',
                         abstract='if running daily, at what time will it run',
                         min_occurs = 0),
            LiteralInput('startdate', 'Start date of runs', data_type='date',
                         abstract='start date of runs'),
            LiteralInput('enddate', 'End date of runs', data_type='date',
                         abstract = 'end date of runs'),
            ]
        outputs = [
            LiteralOutput('FileDir', 'Output file directory', data_type='string',
                          abstract='Location of output files'),
            ComplexOutput('FileContents', 'Output files (zipped)',
                          abstract="Output files (zipped)",
                          supported_formats=[Format('application/x-zipped-shp')],
                          as_reference=True),
            ComplexOutput('ExamplePlot', 'Example Plot of initial time point',
                          abstract='Example plot of initial time point',
                          supported_formats=[Format('image/tiff')],
                          as_reference=True),
            ]

        super(RunNAME, self).__init__(
            self._handler,
            identifier='runname',
            title='Run NAME-on-JASMIN - Advanced',
            abstract="Passes input arguments onto NAME",
            version='0.1',
            metadata=[
                Metadata('NAME-on-JASMIN guide', 'http://jasmin.ac.uk/jasmin-users/stories/processing/'),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True)

    def _handler(self, request, response):

        # Need to process the elevationOut inputs from a list of strings, into an array of tuples.
        ranges = []
        for elevationrange in request.inputs['elevationOut']:
            if '-' in elevationrange.data:
                minrange, maxrange = elevationrange.data.split('-')
                ranges.append((int(minrange), int(maxrange))) # need to error catch int() and min < max
            else:
                raise InvalidParameterValue(
                    'The value "{}" does not contain a "-" character to define a range, '
                    'e.g. 0-100'.format(elevationrange.data))

        LOGGER.debug("domains: %s" % (request.inputs['domain'][0].data))
        domains = []
        for val in request.inputs['domain'][0].data:
            ## Values appear to be coming in as minY, minX, maxY, maxX
            domains.append(float(val))

        params = dict()
        for p in request.inputs:
            if p == 'elevationOut':
                params[p] = ranges
            elif p == 'domain':
                params[p] = domains
            else:
                params[p] = request.inputs[p][0].data

        outdir, zippedfile, mapfile = run_name(params)

        response.outputs['FileContents'].file = zippedfile + '.zip'
        response.outputs['FileDir'].data = outdir
        response.outputs['ExamplePlot'].file = mapfile

        response.update_status("done", 100)
        return response
