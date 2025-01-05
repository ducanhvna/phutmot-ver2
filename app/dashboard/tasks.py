# hrms/tasks.py

import logging
from celery import shared_task
# from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task
def check_apec_hrms_update():
    logger.info(f"Create attendance check apecinpu")
    print("Tác vụ chạy định kỳ mỗi 30 giây check_apec_hrms_update")
    # Thực hiện công việc của bạn tại đây
