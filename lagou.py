# coding = utf-8


from urllib import request, parse
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time

global driver
options = webdriver.ChromeOptions()  # 为浏览器添加设置
options.add_argument('--headless')  # 设置无头即无界面模式
options.add_argument('--disable-gpu')  # 设置不使用gpu加速
options.add_argument('user-agent=Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11')
driver = webdriver.Chrome(chrome_options=options, executable_path='E:\chromedriver\chromedriver.exe')  # executable_path后面填入chromeriver的绝对路径

#  有可能数据太多，爬取过程中出现需要登录的情况，这时候直接网页端登录，把cookie放到这里来
# cookies = {
#     ...
# }
# driver.get('https://www.lagou.com/')  # 这里如果设置cookie的话，需要先加载同domain下的网址，让浏览器知道cookie属于哪个网站
# driver.add_cookie(cookie_dict=cookies)

global jobs_list, companys_list, moneys_list, worker_request_list, company_num_list, job_desc_list
jobs_list = []
companys_list = []
moneys_list = []
worker_request_list = []
company_num_list = []
job_desc_list = []


class LagouSpider(object):
    def __init__(self):
        self.city_name = input("请输入你想要工作的城市：")
        self.job_name = input('请输入你想要找的工作：')
        self.url = 'https://www.lagou.com/jobs/'

    def load_url(self):
        city_name = parse.quote(self.city_name)
        job_name = parse.quote(self.job_name)
        url = self.url + "list_" + job_name + "?city=" + city_name
        print("开始处理。。。")
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")
        self.deal_soup(soup)

    def deal_soup(self, soup):
            jobs = soup.find_all("h3")
            companys = soup.select("div[class='company'] > div > a")
            moneys = soup.find_all("span", class_="money")
            worker_requests = soup.find_all("div", class_="li_b_l")
            company_nums = soup.find_all("div", class_="industry")
            job_descs = soup.find_all("div", class_="li_b_r")
            for job, company, money, worker_request, company_num, job_desc in zip(jobs, companys, moneys, worker_requests, company_nums, job_descs):
                jobs_list.append(job.text)
                companys_list.append(company.text)
                moneys_list.append(money.text)
                worker_request_list.append(worker_request.text)
                company_num_list.append(company_num.text.split('/')[-1])
                job_desc_list.append(job_desc.text)

            # 当这个class属性在源码中搜不到,即值为-1的时候，点击下一页，否则中断
            try:
                if driver.page_source.find("pager_next_disable") == -1:
                    # driver.save_screenshot('jietu.png')  # 可以看到当前页面的截图
                    driver.find_element_by_xpath("//span[@action='next']").click()
                    time.sleep(0.1)
                    soup = BeautifulSoup(driver.page_source, "lxml")
                    self.deal_soup(soup)
                else:
                    print("处理完成。。。")
            except Exception as e:
                print(e)

    def deal_dict(self):
        print("正在写入excel文件。。。")
        dict = {
            '工作': jobs_list,
            '公司': companys_list,
            '公司人数': company_num_list,
            '薪资': moneys_list,
            '要求': worker_request_list,
            '福利': job_desc_list
        }
        table_data = pd.DataFrame(dict)
        table_data.to_excel('job.xls', na_rep='null', index=False)
        print("写入完成，谢谢使用。。。")


if __name__ == '__main__':
    lagou = LagouSpider()
    lagou.load_url()
    lagou.deal_dict()
