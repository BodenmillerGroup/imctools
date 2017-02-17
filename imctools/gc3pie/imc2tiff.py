from imctools.scripts import imc2tiff
from os.path import abspath, basename
import os
import itertools
from gc3libs import Application
from gc3libs.cmdline import SessionBasedScript
from gc3libs.quantity import GB
import gc3libs

class Imc2TiffApp(Application):
    """
    Converts an IMC file to a tiff
    """

    def __init__(self, filename, **kwargs):
        inp = basename(filename)
        script = os.path.split(__file__)[0]
        script = os.path.realpath(script+'/../scripts/imc2tiff.py')

        out = ['@tiff']
        Application.__init__(self,
                             arguments=[script, inp],
                             inputs=[filename],
                             outputs=gc3libs.ANY_OUTPUT,
                             output_dir='test',
                             stdout="stdout.txt",
                             stderr="stderr.txt",
                             requested_memory=1 * GB)


class Imc2TiffScript(SessionBasedScript):
    """
    gc3pie wrapper for Imc2Tiff
    """

    def __init__(self):
        super(Imc2TiffScript, self).__init__(version='0.1')

    def setup_args(self):
        self.add_param('imc_filename', metavar='mcd_filename', type=str,
                            help='The path to the mcd or txt IMC file to be converted')

    def new_tasks(self, extra):
        input_file = self.params.imc_filename
        inputfile = abspath(input_file)

        apps_to_run = []
        apps_to_run.append(Imc2TiffApp(input_file))
        return apps_to_run


if __name__ == '__main__':
    Imc2TiffScript().run()