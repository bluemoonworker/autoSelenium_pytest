#coding=utf-8
import os
import time
import logging
import pytest
import click
from conftest import REPORT_DIR
from config import RunConfig

# logging模块是Python内置的标准模块，主要用于输出运行日志，可以设置输出日志的等级、日志保存路径、日志文件回滚等
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_env(new_report): #初始化测试报告目录
    os.mkdir(new_report)
    os.mkdir(new_report + "/image")


@click.command()
@click.option('-m', default=None, help='输入运行模式：run 或 debug.')

def run(m):
    if m is None or m == "run":
        logger.info("开始执行回归模式——")
        now_time = time.strftime("%Y_%m_%d_%H_%M_%S")
        RunConfig.NEW_REPORT = os.path.join(REPORT_DIR, now_time)
        init_env(RunConfig.NEW_REPORT)
        html_report = os.path.join(RunConfig.NEW_REPORT, "report.html")
        xml_report = os.path.join(RunConfig.NEW_REPORT, "junit-xml.xml")
        pytest.main(["-s", "-v", RunConfig.cases_path,
                     "--html=" + html_report,
                     "--junit-xml=" + xml_report,
                     "--self-contained-html",
                     "--maxfail", RunConfig.max_fail,
                     "--reruns", RunConfig.rerun])
        logger.info("运行结束，生成测试报告！！")
    elif m == "debug":
        print("开始执行调试模式——")
        pytest.main(["-v", "-s", RunConfig.cases_path])
        print("运行结束！！")

if __name__ == '__main__':
    run()