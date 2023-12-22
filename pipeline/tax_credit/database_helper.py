from itertools import islice
from datetime import datetime, timedelta
from math import ceil

from django.db.utils import ProgrammingError
from django.db import connection

from tax_credit.load_job import LoadJob
from common.storage import DataReader
from common.logger import LoggerFactory

logger = LoggerFactory.get(__name__)


class DatabaseHelper:
    @staticmethod
    def load_batched(job: LoadJob, reader: DataReader, load_batch_size, batch_number_of):
        """Loads data for a given job using exponential smoothing to choose batch sizes

        Args:
            job (LoadJob): Corresponds to a cleaned data file and instructions for how to load. Details for jobs are set in `pipeline.yml`
            reader (DataReader): Data reader object to handle the file.
            load_batch_size (int): For smoke test
            batch_number_of (int): For smoke test
        """
        logger.info(f'Loading batch job : {job.job_name}')
        try:

            objs = (
                job.row_to_model(row)
                for row in reader.iterate(job.filename, delimiter=job.delimiter)
            )

            #####

            target_time = timedelta(seconds=5)
            smoothing_factor = 0.1
            #
            batch_ct = 0
            batch_size = 1
            cursor_start_time = datetime.now()
            average_proc_time_per_record = timedelta(seconds=0)
            while True:
                logger.info("Starting load method")

                batch = list(islice(objs, batch_size))
                if not batch:
                    break

                logger.info(f"{job.job_name} batch {batch_ct} - Starting, size {batch_size}")

                # TODO can this connection reset be removed?
                if datetime.now() - cursor_start_time > timedelta(minutes=1):
                    logger.debug("Cursor has been alive too long, resetting")
                    connection.close()
                    cursor_start_time = datetime.now()
                
                st_time = datetime.now()
                if job.unique_fields:
                    job.model.objects.bulk_create(
                        batch,
                        update_conflicts=True,
                        unique_fields=job.unique_fields,
                        update_fields=job.update_fields,
                    )
                else: 
                    job.model.objects.bulk_create(
                        batch,
                        update_fields=job.update_fields,
                    )

                # break for smoketest
                if batch_number_of is not None and batch_ct >= batch_number_of:
                    break
                end_time = datetime.now()
                logger.debug(f"{job.job_name} batch {batch_ct} - Finishing")
                    
                # Calibrate proper batch size
                processing_time = end_time - st_time
                average_proc_time_per_record = (1 - smoothing_factor) * average_proc_time_per_record + smoothing_factor * processing_time / batch_size
                if batch_ct < 5:
                    batch_size = min(ceil(target_time / average_proc_time_per_record), ceil(batch_size * 2))
                else:
                    batch_size = ceil(target_time / average_proc_time_per_record)
                logger.debug(f"{job.job_name} batch {batch_ct} - Processing time : {processing_time}")

                batch_ct += 1
                logger.debug("Ending load method")

        except ProgrammingError as e:
            logger.error(
                f"Could not process [ {job.job_name} ] record. Check row to model transformation: [ {job.row_to_model} ]"
            )

    @staticmethod
    def query_and_cache(model, field, filter):
        # query = model.objects.values(field)
        query = model.objects
        if filter:
            query = query.filter(filter)
        out = list(query.all())
        return out
