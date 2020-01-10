import csv
from array import array
from typing import TextIO, Union

import numpy as np


class TxtParser:
    def __init__(self, fp: Union[str, TextIO]):
        if isinstance(fp, TextIO):
            fp.seek(0)
            self.parse_csv3(fp)
        else:
            with open(fp, "rt") as f:
                self.parse_csv3(f)

    def parse_csv(self, txtfile, first_col=3):
        txtreader = csv.reader(txtfile, delimiter='\t')
        header = txtreader.next()
        channel_names = header[first_col:]
        nchan = len(channel_names)
        txtreader = csv.reader(txtfile, delimiter='\t',
                               quoting=csv.QUOTE_NONNUMERIC)
        txtreader.next()
        data = list()
        for row in txtreader:
            rowar = array.array('f')
            rowar.fromlist(row[first_col:])
            data.append(rowar)
        self.data = np.array(data)
        self.channel_metals = channel_names

    def parse_csv2(self, txtfile, first_col=3):
        header = txtfile.readline().split('\t')
        channel_names = header[first_col:]
        data = [[float(v) for v in row.split('\t')[first_col:]] for row in txtfile]
        self.data = np.array(data)
        self.channel_metals = channel_names

    def parse_csv3(self, file: TextIO, first_column: int = 3):
        """
        The fastest  csv parser so far
        """
        header = file.readline().split('\t')
        channel_names = header[first_column:]
        nchan = len(channel_names)
        rowar = array('f')
        for row in file:
            for v in row.split('\t')[first_column:]:
                rowar.append(float(v))
        nrow = int(len(rowar) / nchan)
        data = [rowar[(i * nchan):(i * nchan + nchan)] for i in range(nrow)]
        self.data = np.array(data)
        self.channel_labels = channel_names


if __name__ == '__main__':
    import timeit

    tic = timeit.default_timer()
    result = TxtParser("/home/anton/Downloads/for Anton/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2/IMMUcan_Batch20191023_10032401-HN-VAR-TIS-01-IMC-01_AC2_pos1_6_6.txt")
    print(timeit.default_timer() - tic)
    pass
