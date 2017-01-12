from __future__ import absolute_import, unicode_literals
import os
import laiutils
from celeryutils import tasks
# from celery import Celery

# app = Celery(broker="ampq://guest:guest@localhost:5672",
#              include=["celeryutils.tasks"])

# CGI with nearest in-LAC CGI
# CGIs that don't have another CGI in-LAC within 30km


def main():
    tgt_job = laiutils.FeedProcessor.process_source_file
    twilio_object = laiutils.TwilioCarriers(os.getenv("TWILIO_SID"),
                                            os.getenv("TWILIO_TOKEN"))
    twilio_object.initialize_carrier_reference("US")
    carrier_reference = twilio_object.carrier_reference
    fp = laiutils.FeedProcessor(carrier_reference)
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_list = [in_file for in_file in laiutils.Utility.get_source_files_from_dir(fp.source_dir)]
    print len(file_list)
    for target_file in file_list:
        tasks.process_feed_file.delay(target_file, carrier_reference, base_path)
    print("Done!")

if __name__ == "__main__":
    main()
