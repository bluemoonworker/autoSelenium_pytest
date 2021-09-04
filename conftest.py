import os
import pytest
from py.xml import html
from selenium import webdriver
from selenium.webdriver import Remote
from selenium.webdriver.chrome.options import Options as ChromeOptions
from config import RunConfig

#项目目录设置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = BASE_DIR+"/test_report/"

#设置用例描述表头
def pytest_html_results_table_header(cells):
    cells.insert(2,html.th('Description'))
    cells.pop()

#设置用例描述表格
def pytest_html_results_table_row(report, cells):
    cells.insert(2, html.td(report.description))
    cells.pop()

@pytest.mark.hookwrapper
#该装饰器的钩子函数，有以下两个作用：
#（1）可以获取到测试用例不同执行阶段的结果（setup，call，teardown）
#（2）可以获取钩子方法的调用结果（yield返回一个result对象）和调用结果的测试报告（返回一个report对象）

def pytest_runtest_makereport(item): #向测试用例中添加用例的开始时间，内部注释和失败截图等
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)#获取的是测试方法的__doc__属性,也就是,测试函数下的注释如"""  """中的内容
    extra = getattr(report, 'extra', [])
    if report.when == 'call' or report.when == "setup":
        xfail = hasattr(report, 'wasxfail')#显式的声明一个用例会失败，如果确实失败，则测试结果显示为通过
        if (report.skipped and xfail) or (report.failed and not xfail):
            case_path = report.nodeid.replace("::", "_") + ".png"
            if "[" in case_path:
                case_name = case_path.split("-")[0] + "].png"
            else:
                case_name = case_path
            capture_screenshots(case_name)#用例失败截图
            img_path = "image/" + case_name.split("/")[-1]
            if img_path:#添加<img>标签，通过src属性指定图片的路径
                html = '<div><img src="%s" alt="screenshot" style="width:304px;height:228px;" ' \
                       'onclick="window.open(this.src)" align="right"/></div>' % img_path
                extra.append(pytest_html.extras.html(html))
        report.extra = extra


def capture_screenshots(case_name): #配置失败后截图保存的路径
    global driver
    file_name = case_name.split("/")[-1]
    if RunConfig.NEW_REPORT is None:
        raise NameError('没有初始化测试报告目录')
    else:
        image_dir = os.path.join(RunConfig.NEW_REPORT, "image", file_name)
        RunConfig.driver.save_screenshot(image_dir)

#启动浏览器
@pytest.fixture(scope='session', autouse=True)

def browser(): #全局定义浏览器驱动

    global driver

    if RunConfig.driver_type == "chrome":
        # 本地chrome浏览器
        driver = webdriver.Chrome()
        driver.maximize_window()

    elif RunConfig.driver_type == "chrome-headless":
        # chrome headless模式
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-gpu')
        #chrome_options.add_argument("--window-size=1920x1080")
        driver = webdriver.Chrome(options=chrome_options)

    elif RunConfig.driver_type == "grid":
        # 通过远程节点运行
        driver = Remote(command_executor='http://localhost:4444/wd/hub',
                        desired_capabilities={
                              "browserName": "chrome",
                        })
        driver.set_window_size(1920, 1080)

    else:
        raise NameError("driver驱动类型定义错误！")

    RunConfig.driver = driver

    return driver

# 关闭浏览器
@pytest.fixture(scope="session", autouse=True)
def browser_close():
    yield driver
    driver.quit()
    print("test end!")


if __name__ == "__main__":
    capture_screenshots("test_dir/test_baidu_search.test_search_python.png")
























