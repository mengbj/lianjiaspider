# -*- coding: utf-8 -*-
"""
"""
import score
import re
import urllib2
from itertools import izip_longest
import random
from multiprocessing import Pool, Process
from bs4 import BeautifulSoup
from collections import defaultdict
import sys

reload(sys)
sys.setdefaultencoding("utf-8")
import os
from datetime import datetime
import time

basedir = os.path.abspath(os.path.dirname('.'))
import _mysql
import MySQLdb as mdb

DBINFO = {
    "host": "127.0.0.1",
    "port": 3306,
    "db": "lianjia",
    "user": "root",
    "passwd": "123456",
    "autocommit": True
}
conn = mdb.connect(**DBINFO)
conn.autocommit(1)
cursor = conn.cursor()
# 登录，不登录不能爬取三个月之内的数据
# import LianJiaLogIn


# Some User Agents
hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}, \
       {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'}, \
       {
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'}, \
       {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'}, \
       {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'}, \
       {'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]

# 北京区域列表
regions = [u"东城", u"西城", u"朝阳", u"海淀", u"丰台", u"石景山", u"通州", u"昌平", u"大兴", u"亦庄开发区", u"顺义", u"房山", u"门头沟", u"平谷", u"怀柔",
           u"密云", u"延庆", u"燕郊"]
regions_dict = {
    'region0': [u"东城"],
    'region1': [u"西城"],
    'region2': [u"朝阳"],
    'region3': [u"海淀"],
    'region4': [u"丰台", u"石景山"],
    'region5': [u"通州", u"昌平"],
    'region6': [u"大兴", u"亦庄开发区", u"顺义", u"房山", u"门头沟", u"平谷", u"怀柔", u"密云", u"延庆", u"燕郊"],
    'region7': []
}


def xiaoqu_detail_spider(url, f):
    """
    爬取小区详细的信息，比如物业信息等
    """
    try:
        soup = get_soup(url)
    except:
        print url, 'xiaoqu_detail_spider', '1' * 50
        return
    xiaoqu_bases = list()
    types = ['title', 'houseInfo', 'positionInfo', 'tagList']
    try:
        xiaoqu_list = soup.find_all('div', {'class': 'xiaoquInfo'})
    except:
        xiaoqu_list = list()
    for i, xiaoqu in enumerate(xiaoqu_list):
        xq = xiaoqu.find_all('div', {'class': 'xiaoquInfoItem'})
        for info1 in xq:
            info2 = info1.find_all('span')
            tmp = list()
            for info1 in info2:
                content = info1.string
                if type(content) == type(None):
                    continue
                tmp.append(content)
                if type(content) != type(None):
                    lnglat = info1.get('mendian')
            print ': '.join(tmp)
            xiaoqu_bases.append(': '.join(tmp))
            f.write('    ' + ': '.join(tmp))
        f.write('    ' + '坐标: %s' % lnglat)

    # 小区均价 月份
    try:
        avg_price = soup.find('div', {'class': 'xiaoquPrice clear'}).find_all('span')
    except:
        return
    avg_price_month = list()
    for price_month in avg_price:
        avg_price_month.append(price_month.string)
    nums_cols1 = [u'小区均价', u'月份']
    for m, n in izip_longest(nums_cols1, avg_price_month):
        if type(n) == type(None):
            n = '-'
        print ': '.join([m, n])
        f.write('    ' + ': '.join([m, n]))

    return xiaoqu_bases


def str_replace(str):
    return str.replace('\n', ' ').replace('/', '').replace(' ', '').strip()


def xiaoqu_spider(region, url_page, base_file, date):
    """
    爬取页面链接中的小区信息
    """
    try:
        soup = get_soup(url_page)
    except:
        print url_page, 'xiaoqu_spider', '2' * 50
        return
    # print '3' * 30
    # 小区ID [小区名称，链接，建成时间，建筑类型，物业费用，物业公司，开发商，楼栋总数，总户数，附近门店，总户型，30天成交套数，优点，info1,info2]
    with open(base_file, 'a') as f:
        xiaoqu_dict = defaultdict(list)
        types = ['title', 'houseInfo', 'positionInfo', 'tagList']
        try:
            xiaoqu_list = soup.findAll('div', {'class': 'info'})
        except:
            xiaoqu_list = []
        for i, xiaoqu in enumerate(xiaoqu_list):
            # print xiaoqu.prettify()
            print '~' * 30
            try:
                xq = xiaoqu.find_all('div', {'class': 'title'})
            except:
                continue
            for info1 in xq:
                xiaoqu_name = info1.a.string.encode('utf8')
                url = info1.a.get('href')
                xiaoqu_id = str(url).split('/')[-2]
                f.write('url: ' + url)
                f.write('    ' + '小区ID: %s' % xiaoqu_id)
                f.write('    ' + '小区名称: %s' % xiaoqu_name)
                xiaoqu_bases = xiaoqu_detail_spider(url, f)

            try:
                xq = xiaoqu.find_all('div', {'class': 'houseInfo'})
            except:
                continue
            # 总户型数  30天成交套数 正在出租套数
            xiaoqu_info1 = list()
            for info2 in xq:
                for key in info2.find_all('a'):
                    xiaoqu_info1.append(key.string)
            nums_cols1 = [u'户型', u'成交', u'出租']
            for m in nums_cols1:
                n_str = '-'
                for n in xiaoqu_info1:
                    if m in n:
                        n_str = n
                f.write('    ' + '%s: %s' % (m, n_str))

            # 地铁
            xq = xiaoqu.find_all('div', {'class': 'tagList'})
            for info2 in xq:
                # print info2, '~'*30, info2.span
                try:
                    print info2.span.string
                    f.write('    ' + '地铁: %s' % (info2.span.string))
                except:
                    f.write('    ' + '地铁: %s' % ('-'))
            f.write('    ' + 'region: %s' % region)
            f.write('    ' + 'date: %s' % date)
            f.write('\n')


def del_table(type, date):
    del_sql = """delete from {type} where date={date}""".format(type=type, date=date)
    try:
        print del_sql
        cursor.execute(del_sql)
    except:
        print '执行SQL有误'


def read_xiaoqu(date):
    base_file = get_file('xiaoqu', date)
    del_table('xiaoqu', date)
    ins_sql = """insert into xiaoqu
        (url, xiaoqu_id, xiaoqu_name, build_age, bulid_type, service_price, service_company, developers, bulid_total, 
        house_total, near_zhongjie, lnglat, avg_price, refer_month, house_type_total, day30_done, rent_num, subway, region, date) values 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

    datas = []
    flags = set()
    with open(base_file, 'rt') as f:
        for tmp in f:
            break_flag = 0
            line = tmp.replace('\n', '')
            # print len(line.split('    '))
            eles = line.split('    ')
            if len(eles) == 20:
                info = []
                for i in range(20):
                    try:
                        ele = eles[i].split(': ')[1]
                        info.append(ele)
                    except:
                        break_flag = 1
            else:
                if len(line.split('    ')) > 1:
                    print len(line.split('    ')), '!' * 30, eles[1]
                continue
            if break_flag:
                continue
            info = escape_string(info)
            [url, xiaoqu_id, xiaoqu_name, build_age, bulid_type, service_price, service_company, developers,
             bulid_total, house_total, near_zhongjie, lnglat, avg_price, refer_month, house_type_total, day30_done,
             rent_num, subway, region, date] = info
            print url, xiaoqu_id, xiaoqu_name, build_age, bulid_type, service_price, service_company, developers, bulid_total, house_total, near_zhongjie, lnglat, avg_price, refer_month, house_type_total, day30_done, rent_num, subway, region, date, '~' * 20
            if xiaoqu_id in flags:
                print 'Notice!!!', url, xiaoqu_id, xiaoqu_name, build_age, bulid_type, service_price, service_company, developers, bulid_total, house_total, near_zhongjie, lnglat, avg_price, refer_month, house_type_total, day30_done, rent_num, subway, region, date
                print '*' * 30
                continue
            flags.add(xiaoqu_id)

            tmp = (
            url, xiaoqu_id, xiaoqu_name, build_age, bulid_type, service_price, service_company, developers, bulid_total,
            house_total, near_zhongjie, lnglat, avg_price, refer_month, house_type_total, day30_done, rent_num, subway,
            region, date)
            datas.append(tmp)
            if len(datas) == 10:
                try:
                    cursor.executemany(ins_sql, datas)
                except Exception, e:
                    print e
                    print '!' * 30
                datas = []
    if len(datas) > 0:
        cursor.executemany(ins_sql, datas)
    print 'ershoufang: Done', '~' * 50
    # 关闭游标连接
    cursor.close()
    # 关闭数据库连接
    conn.close()


def do_xiaoqu_spider(date):
    """
    爬取大区域中的所有小区信息
    """
    p = Pool(8)
    base_file = get_file('xiaoqu', date)
    with open(base_file, 'wt') as f:
        f.write('')
    for region in regions:
        url = u"http://bj.lianjia.com/xiaoqu/rs" + region + "/"
        print url, '1' * 30
        try:
            soup = get_soup(url)
        except:
            print url, 'do_xiaoqu_spider', '3' * 50
            continue
        total_pages = get_pages(soup)
        if total_pages == 0:
            continue
        p.apply_async(single_process_xiaoqu, args=(base_file, region, total_pages,))
        print u"爬下了 %s 区全部的小区信息" % region
    p.close()
    p.join()


def single_process_xiaoqu(base_file, region, total_pages):
    for i in range(total_pages):
        url_page = u"http://bj.lianjia.com/xiaoqu/pg%drs%s/" % (i + 1, region)
        print url_page, '2' * 30
        xiaoqu_spider(region, url_page, base_file, date)


def get_pages(soup):
    try:
        d = "d=" + soup.find('div', {'class': 'page-box house-lst-page-box'}).get('page-data')
        exec (d)
        total_pages = d['totalPage']
    except:
        total_pages = 0
    return total_pages




def split_str(lists):
    for key in lists:
        if key:
            return key


def get_urls(type):
    """
        1、爬取北京有哪些区域，比如朝阳区；
        2、进一步这些区域细分到各个片区，比如朝阳区下的北苑；
        这么处理的原因是解决，链家在展示二手房时仅仅展示前3000套房的限制，导致数据抓取不全的问题；
        3、取到片区后，再爬取各片区每一页对应的房源数据
    """
    urls = defaultdict(dict)
    # 1、爬取北京有哪些区域，比如朝阳区；
    url_region = 'https://bj.lianjia.com/{type}/'.format(type=type)
    soup_region = get_soup(url_region)
    regions = soup_region.find('div', {'class': 'sub_nav section_sub_nav'}).find_all('a')

    # 使用多协程
    from gevent import monkey
    import gevent
    monkey.patch_all()
    tasks = list()
    for region in regions:
        tasks.append(gevent.spawn(get_region_area_gevent, urls, region))
        print tasks
    gevent.joinall(tasks)
    return urls


def get_region_area_gevent(urls, region):
    region_name = region.string
    # if region_name != u'朝阳':
    #     continue

    region_url = region.get('href')
    # 2、进一步这些区域细分到各个片区，比如朝阳区下的北苑；
    url_area = 'https://bj.lianjia.com' + region_url
    soup_area = get_soup(url_area)
    try:
        areas = soup_area.find('div', {'class': 'sub_sub_nav section_sub_sub_nav'}).find_all('a')
    except Exception, e:
        print e
        print region_name
        return
    for area in areas:
        area_name = area.string
        area_url = area.get('href')
        # if area_name !=u'太阳宫':
        #     continue

        # 3、取到片区后，再爬取各片区每一页对应的房源数据
        area_url = 'https://bj.lianjia.com' + area_url
        soup_page = get_soup(area_url)
        total_pages = get_pages(soup_page)
        if not total_pages:
            continue
        print region_name, area_name, area_url
        urls[region_name][area_name] = [area_url, total_pages]


def get_soup(url):
    try:
        req = urllib2.Request(url, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib2.urlopen(req, timeout=5).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        return ''
    except Exception, e:
        print e
        return
    return soup


def get_file(type, date):
    time.sleep(5)
    # basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = '/Users/mengbangjie/lianjia/LianJiaLogs'
    base_path = basedir + '/%s/' % type + date
    # if not os.path.exists(base_path):
    #     os.mkdir(base_path)
    base_file = base_path + '.txt'
    return base_file


def escape_string(*encode_args):
    encodes = list()
    for encode_arg in encode_args[0]:
        # print type(encode_args), encode_args, '1'*30
        # print type(encode_arg), encode_arg, '2'*30
        if encode_arg:
            encode = _mysql.escape_string(encode_arg)
        else:
            encode = '-'
        encodes.append(encode)
    return encodes



if __name__ == "__main__":
    date = datetime.now().strftime('%Y%m%d')
    # date='20180430'
    print date
    start = time.time()
    if len(sys.argv) == 2:
        types = sys.argv[1]
    if types == 'xiaoqu':
        # 爬下所有的小区信息
        do_xiaoqu_spider(date)
        read_xiaoqu(date)
    end = time.time()
    print "抓取{types}耗时：{diff}秒".format(types=types, diff=int(end - start))
