import gc3libs
from gc3libs import Application, Run, Task
from gc3libs.cmdline import SessionBasedScript, _Script
from gc3libs.workflow import SequentialTaskCollection, ParallelTaskCollection
import gc3libs.utils

class GenerateAnalysisStack(Application):
    def __init__(self, img, pannelcsv, metalcolumn):
        arguments = ["python -m imctools.scripts.ometiff2analysis", img, '--outpostfix',]


        gc3libs.Application.__init__(self,
                                     arguments = arguments,
                                     inputs = {tarfile_name:os.path.basename(tarfile_name)},
                                     outputs = [],
                                     output_dir = os.path.join(output_folder,str(param_value),str(iteration),"POST"),
                                     join = True,
                                     stdout = "stdout.log",
                                     **extra_args
                                     )