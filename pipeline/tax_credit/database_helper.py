from itertools import islice
from datetime import datetime, timedelta
from math import ceil

from django.db.utils import ProgrammingError

from tax_credit.load_job import LoadJob
from common.storage import DataReader
from common.logger import LoggerFactory

logger = LoggerFactory.get(__name__)


class DatabaseHelper:
    @staticmethod
    def load_batched(job: LoadJob, reader: DataReader, load_batch_size, batch_number_of):
        logger.info(f'Loading batch job : {job.job_name}')
        try:
            objs = (
                job.row_to_model(row)
                for row in reader.iterate(job.filename, delimiter=job.delimiter)
            )

            #####

            batch_ct = 0
            is_calibrated = False
            batch_size = 1
            target_time = timedelta(seconds=15)
            max_time = timedelta(seconds=60)
            while True:
                logger.info(f"Starting batch {batch_ct}")
                batch = list(islice(objs, batch_size))
                if not batch:
                    break
                
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
                    
                # Calibrate proper batch size
                processing_time = end_time - st_time
                logger.info(f"Finished batch {batch_ct}")
                logger.info(f"Batch {batch_ct} processing time : {processing_time}")
                if not is_calibrated and abs(processing_time - target_time) <= timedelta(seconds=3):
                        is_calibrated = True
                        target_time = max_time
                # Adjust the batch size to be closer to the desired length of processing time
                batch_size = ceil(batch_size * (target_time / processing_time))

                batch_ct += 1

            #####

            # batch_ct = 0
            # while True:
            #     logger.info(f"Loading batch {batch_ct + 1} for {job.job_name}")
            #     batch = list(islice(objs, load_batch_size))
            #     if not batch:
            #         break
            #     if job.unique_fields:
            #         job.model.objects.bulk_create(
            #             batch,
            #             update_conflicts=True,
            #             unique_fields=job.unique_fields,
            #             update_fields=job.update_fields,
            #         )
            #     else: 
            #         job.model.objects.bulk_create(
            #             batch,
            #             update_fields=job.update_fields,
            #         )
            #     batch_ct += 1
            #     if batch_number_of is not None and batch_ct >= batch_number_of:
            #         break
        except ProgrammingError as e:
            logger.error(
                f"Could not process [ {job.job_name} ] record. Check row to model transformation: [ {job.row_to_model} ]"
            )
            # logger.error(f"ERROR : {e}")

    @staticmethod
    def query_and_cache(model, field, filter):
        # query = model.objects.values(field)
        query = model.objects
        if filter:
            query = query.filter(filter)
        out = list(query.all())
        return out
