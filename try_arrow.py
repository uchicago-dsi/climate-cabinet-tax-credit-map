import os
import pyarrow.parquet as pq
from django.contrib.gis.geos import GEOSGeometry
import time
import datetime
from pprint import pprint



def parquet_iterator(file_name, batch_size):
    """
    The geoparquet files are too large to load directly with geopandas and there does not appear to be a way to chunk them.
    This uses pyarrow to create a generator that will return chunks of rows that can be loaded with less overhead.
    Additionally, it converts WKB geometry representations to GEOSGeometry objects that Django is able to handle.
    Note that it will SPECIFICALLY look for a column named 'geometry' to convert and no others.

    params:
        file_name: name of the geoparquet file to read
        batch_size: this is the batch size of both the batches of rows that that the generator returns and the batch size that are retrieved from the parquet
    """
    pf = pq.ParquetFile(file_name)
    col_names = pf.schema.names
    geom_col_index = col_names.index('geometry')

    batches = pf.iter_batches(batch_size)
    for columns in batches:

        py_row_batch = []
        for arrow_row in zip(*columns):
            py_row = []
            for idx, r in enumerate(arrow_row):
                if idx == geom_col_index:
                    py_row.append(GEOSGeometry(memoryview(r.as_py())))
                else:
                    py_row.append(r.as_py())
            py_row_batch.append(py_row)
        yield py_row_batch
    
    pf.close()

if __name__ == "__main__":
    batch_size = 1_000 # seems about optimal -- on 10 run arithmetic average not a big difference between 100 and 10_000
    for batch in parquet_iterator("data/justice40.geoparquet", batch_size):
        for row in batch:
            print(row)
        time.sleep(.2)
