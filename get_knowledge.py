
import queue
import time
import threading
import requests
import pymongo
import logging
import os

# 配置用于日志打印的 logger，纯属个人爱好，你可以用 print 代替
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

if __name__ == '__MAIN__':
    try:
        # 打开数据库连接
        logger.info('Connecting to MongoDB...')
        client = pymongo.MongoClient(MONGODB_URI)
        logger.info('Successfully connected!')

        # 在此进行爬虫逻辑

        # 关闭数据库连接
        logger.info('Closing MongoDB...')
        client.close()
        logger.info('Successfully closed!')
    except Exception as e:
        logger.error(e)
