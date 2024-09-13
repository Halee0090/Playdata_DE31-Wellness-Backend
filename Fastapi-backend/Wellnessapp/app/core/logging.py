import logging

def setup_logging():
    # 로깅설정
    logging.basicConfig(
        level=logging.DEBUG,
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers = [
            logging.FileHandler('app.log', mode='w'),  # 로그 파일에 기록
            logging.StreamHandler()  # 콘솔에 로그 출력
        ]
    )
    
    logger = logging.getLogger("main")
    return logger