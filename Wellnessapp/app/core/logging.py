import logging
import pytz
from datetime import datetime

# 한국 표준시(KST) 타임존 설정
KST = pytz.timezone('Asia/Seoul')

# 로그 시간에 KST 타임존 적용
class KSTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        kst_time = datetime.now(KST)
        if datefmt:
            return kst_time.strftime(datefmt)
        else:
            return kst_time.strftime("%Y-%m-%d %H:%M:%S")

# 로깅 설정
formatter = KSTFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 테스트 로그 출력
logger.info("KST 타임존 로그 테스트")
