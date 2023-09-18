import pyarrow.parquet as pq
import pyarrow

from itertools import islice


def main():
    

    def batcher(filename, chunk_size=1_000):
        try:
            pf = pq.ParquetFile(filename)
            print(pf.schema)
            pf_iter = pf.iter_batches(chunk_size)
            for batch in pf_iter:
                row_list = batch.to_pylist()
                for row in row_list:
                    row.pop('geometry')
                    yield row
        finally:
            pf.close()
    
    def metadata(filename):
        pf = pq.ParquetFile(filename)
        # for t in pf.schema:
            # print(t.physical_type)
            # print([)
        print([t.name for t in pf.schema])
    
    metadata('data/justice40.geoparquet')

    # rows = batcher('data/justice40.geoparquet')
    # for row in rows:
        # print(row)
        





if __name__ == '__main__':
    main()