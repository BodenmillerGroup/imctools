from __future__ import with_statement, division

import os
from imcacquisitionbase import ImcAcquisitionBase

class ImcTextAcquisitionBase(ImcAcquisitionBase):
    """
    Loads and strores an IMC .txt file
    """

    def __init__(self, filename):
        super(ImcAcquisitionBase, self).__init__()

