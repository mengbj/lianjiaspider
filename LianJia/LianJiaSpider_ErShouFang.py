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


def del_table(type, date):
    del_sql = """delete from {type} where date={date}""".format(type=type, date=date)
    try:
        print del_sql
        cursor.execute(del_sql)
    except:
        print '执行SQL有误'


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


def ershoufang_spider(base_file, url, date):
    """
    爬取页面链接中的二手房记录
    """
    soup = get_soup(url)
    with open(base_file, 'a') as f:
        # f.write('\n'+'~~~~~~~~~' * 20)
        f.write("url: %s" % url)
        print '~~~~~~~~~' * 20
        print url
        house_id = str(url).split('/')[-1].split('.html')[0]
        f.write('    ' + "house_id: %s" % house_id)
        info_dict = defaultdict()
        info_dict['url'] = url
        try:
            sell_title = soup.find_all('div', {'class': 'sellDetailHeader'})
        except:
            return
        for title_actinos in sell_title:
            # 卖房的标题
            title = title_actinos.find('h1', {'class': 'main'}).string
            subtitle = title_actinos.find('div', {'class': 'sub'}).string
            print '主标题: %s' % title
            print '副标题: %s' % subtitle
            f.write('    ' + '主标题: %s' % title)
            f.write('    ' + '副标题: %s' % subtitle)
            info_dict['title'] = ['主标题: %s' % title, '副标题: %s' % subtitle]
            # 关注量和预约量
            try:
                actions = title_actinos.find_all('div', {'class': 'action'})
            except:
                actions = list()
            info_dict['buyer_nums'] = []
            for action in actions:
                button_num = list()
                button = action.button.string
                num = action.span.string
                nums = ': '.join([button, num])
                print nums
                f.write('    ' + nums)
                info_dict['buyer_nums'].append(nums)
        # 小区名称 所在位置 看房时间
        try:
            xiaoqu_names = soup.find('div', {'class': 'communityName'}).find('a', {'class': 'info'}).string
        except:
            xiaoqu_names = '-'
        print '小区名称: %s' % xiaoqu_names
        f.write('    ' + '小区名称: %s' % xiaoqu_names)
        info_dict['xiaoqu_names'] = xiaoqu_names

        # 所在位置
        locs = list()
        try:
            xiaoqu_location = soup.find('div', {'class': 'areaName'}).find('span', {'class': 'info'})
        except:
            xiaoqu_location = list()

        for location in xiaoqu_location:
            import unicodedata
            try:
                location = unicodedata.normalize('NFKD', location.string).encode('utf-8', 'ignore')
            except:
                location = ''
            loc = location.replace(' ', '')
            if loc:
                locs.append(loc)
        locs_cols = [u'区域', u'片区', u'环数']
        for m, n in izip_longest(locs_cols, locs):
            if type(n) == type(None):
                n = '-'
            print ': '.join([m, n])
            f.write('    ' + ': '.join([m, n]))

        # 地铁
        try:
            subway = soup.find('div', {'class': 'areaName'}).find('a', {'class': 'supplement'}).string
        except:
            subway = '-'
        if type(subway) == type(None):
            subway = '-'
        print '地铁: %s' % subway
        f.write('    ' + '地铁: %s' % subway)
        info_dict['subway'] = subway

        info_dict['base_info'] = []
        # 总价
        try:
            prices = soup.find_all('div', {'class': 'price'})
            for price in prices:
                total = price.span.string  # + u'万'
                print '总价: %s' % total
        except:
            total = '-'
        f.write('    ' + '总价: %s' % total)
        info_dict['base_info'].append('总价: %s' % total)
        # 基本属性
        try:
            bases = soup.find_all('div', {'class': 'base'})
        except:
            bases = []
        for base in bases:
            conts = base.find('div', {'class': 'content'}).find('ul')
            for cont in conts:
                # NavigableString按照字面意义上理解为可遍历字符串，注意此时cont的数据类型
                base_title, base_content = '-', '-'
                for i, key in enumerate(cont):
                    if i == 0 and type(key) != unicode:
                        base_title = key.string
                    if i == 1:
                        base_content = key
                        base_res = ': '.join([base_title, base_content])
                        print base_res
                        f.write('    ' + base_res)
                        info_dict['base_info'].append(base_res)
        info_dict['transaction_info'] = []
        # 交易属性
        try:
            transactions = soup.find_all('div', {'class': 'transaction'})
        except:
            transactions = []
        for transaction in transactions:
            conts = transaction.find('div', {'class': 'content'}).find('ul')
            for i, cont in enumerate(conts.find_all('li')):
                titles_contents = cont.find_all('span')
                transaction_tmp = list()
                for titles_content in titles_contents:
                    tcs = titles_content.string
                    # 过滤空格或换行符
                    tcs = split_str(re.split(r'[\n\s]', tcs))
                    transaction_tmp.append(tcs)
                print ': '.join(transaction_tmp)
                f.write('    ' + ': '.join(transaction_tmp))
                info_dict['transaction_info'].append(': '.join(transaction_tmp))
        # 户型分布
        try:
            houses = soup.find('div', {'id': 'infoList'})
            houses = houses.find_all('div', {'class': 'col'})  # , type(houses), '00'*30
            house_area_tmp = []
            info_dict['house_info'] = []
            house_info = []
            house_info_str = []

            print '房间类型 面积 朝向 窗户'
            # f.write('\n' + '房间类型 面积 朝向 窗户')
            for i, house in enumerate(houses):
                house_area_direction = house.string
                house_area_tmp.append(house_area_direction)
                if (i - 3) % 4 == 0:
                    house_area = ', '.join(house_area_tmp)
                    house_info.append(house_area)
                    print house_area
                    # f.write('\n' + house_area)
                    info_dict['house_info'].append(house_area)
                    house_area_tmp = []
            f.write('    ' + "house_info: %s" % '||'.join(house_info))
            # print '  '.join(house_info)
        except:
            f.write('    ' + "house_info: -")
            info_dict['house_info'] = []
        # for key in info_dict:
        #     print key, info_dict[key]
        f.write('    ' + 'date: %s' % date)
        f.write('\n')
        return ''


def do_ershoufang_spider(region, date):
    time_start = time.time()
    base_file = get_file('ershoufang', date)
    with open(base_file, 'wt') as f:
        f.write('')
    urls_dict = get_urls('ershoufang')
    time_end = time.time()
    time_diff = time_end - time_start
    print "耗时:%d" % time_diff
    print '0' * 20
    # p = Pool(8)
    print "1" * 20
    NUM = 5
    for region in urls_dict:
        print region, "2" * 20
        for i, area in enumerate(urls_dict[region]):
            pages_url, total_pages = urls_dict[region][area]
            # total_pages = 1
            # 暂时执行单任务
            p = Process(target=single_process_ershoufang, args=(base_file, pages_url, total_pages,))
            print('%s-%s Child process will start' % (region, area)), '~' * 20
            print '1' * 20, i
            p.start()
            print '2' * 20, i
            if not i % NUM == 0:
                try:
                    p.join()
                except Exception, e:
                    print e, '!!' * 20
    p.join()

    # 多进程池
    #         p.apply_async(single_process_ershoufang, args=(base_file, pages_url, total_pages,))
    # p.close()
    # p.join()


def single_process_ershoufang(base_file, pages_url, total_pages):
    for i in range(total_pages):
        url = pages_url + "pg%d" % (i + 1)
        print url
        try:
            soup = get_soup(url)
            # 获取所有二手房的链接
            tmp = soup.find_all('div', {'class': 'title'})
        except:
            continue
        for urls in tmp:
            for key in urls:
                # print region,area,key,'3'*20
                # print key.get('href'), '~' * 10
                try:
                    url = key.get('href')
                except:
                    continue
                if not url:
                    continue
                # print url, '~' * 10
                ershoufang_spider(base_file, url, date)


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


def read_ershoufang(date):
    base_file = get_file('ershoufang', date)
    del_table('ershoufang', date)
    ins_sql = """insert into ershoufang
        (url, house_id, title, subtitle, buyer_attention, buyer_see, xiaoqu_name, region, area, ring_road, subway, 
        total, house_type, floor, bulid_area,house_structure, use_area, bulid_type, orientation, build_structure,
        fitment, ladder_rate, warm, lift, property_right_year, createtime, property, last_buy_time, house_use, 
        house_limit, property_right_belong, pledge_info, supplement, house_info, date, defang_area, total_score, 
        defang_score, huxing_score, chuanghu_score, chaoxiang_score, defang_rate, defang_price_score, defang_price, fitment_score) values 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s) """

    datas = []
    info = []
    j = 0
    flags = set()
    with open(base_file, 'rt') as f:
        for tmp in f:
            break_flag = 0
            line = tmp.replace('\n', '')
            # print len(line.split('    '))
            eles = line.split('    ')
            if len(eles) == 35:
                info = []
                for i in range(35):
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
            [url, house_id, title, subtitle, buyer_attention, buyer_see, xiaoqu_name, region, area, ring_road, subway,
             total, house_type, floor, bulid_area,
             house_structure, use_area, bulid_type, orientation, build_structure, fitment, ladder_rate, warm, lift,
             property_right_year,
             createtime, property, last_buy_time, house_use, house_limit, property_right_belong, pledge_info,
             supplement, house_info, date] = info
            # 评分相关
            total_score, defang_score, huxing_score, chuanghu_score, chaoxiang_score, defang_area, defang_rate, defang_price_score, defang_price, fitment_score = score.get_score(
                house_info, bulid_area, total, fitment)

            if house_id in flags:
                # print '*'*30
                continue
            flags.add(house_id)

            tmp = (
                url, house_id, title, subtitle, buyer_attention, buyer_see, xiaoqu_name, region, area, ring_road,
                subway,
                total,
                house_type, floor, bulid_area.replace('㎡', ''), house_structure, use_area.replace('㎡', ''),
                bulid_type, orientation, build_structure, fitment, ladder_rate, warm, lift, property_right_year,
                createtime, property, last_buy_time, house_use, house_limit, property_right_belong, pledge_info,
                supplement,
                house_info, date, defang_area, total_score, defang_score, huxing_score, chuanghu_score, chaoxiang_score,
                defang_rate, defang_price_score, defang_price, fitment_score)
            datas.append(tmp)
            if len(datas) == 10:
                try:
                    cursor.executemany(ins_sql, datas)
                except Exception, e:
                    print e
                    # print '!'*30
                datas = []
    if len(datas) > 0:
        cursor.executemany(ins_sql, datas)
    print 'ershoufang: Done', '~' * 50
    # 关闭游标连接
    cursor.close()
    # 关闭数据库连接
    conn.close()


def read_ershoufang_price(date):
    base_file = get_file('ershoufang', date)
    del_table('ershoufang_price', date)
    ins_sql = """insert into ershoufang_price
        (house_id, buyer_attention, buyer_see, total, date) values (%s, %s, %s, %s, %s) """

    datas = []
    info = []
    flags = set()

    with open(base_file, 'rt') as f:
        for tmp in f:
            break_flag = 0
            line = tmp.replace('\n', '')
            # print len(line.split('    '))
            eles = line.split('    ')
            if len(eles) == 35:
                info = []
                for i in range(35):
                    try:
                        ele = eles[i].split(': ')[1]
                        info.append(ele)
                    except:
                        break_flag = 1
            else:
                print len(line.split('    ')), '!' * 30
                continue

            if break_flag:
                continue

            info = escape_string(info)
            [url, house_id, title, subtitle, buyer_attention, buyer_see, xiaoqu_name, region, area, ring_road, subway,
             total, house_type, floor, bulid_area,
             house_structure, use_area, bulid_type, orientation, build_structure, fitment, ladder_rate, warm, lift,
             property_right_year,
             createtime, property, last_buy_time, house_use, house_limit, property_right_belong, pledge_info,
             supplement, house_info, date] = info
            # print url, house_id, title, subtitle, buyer_attention, buyer_see, xiaoqu_name, total, house_type, floor, bulid_area,house_structure, use_area, bulid_type, orientation, build_structure, fitment, ladder_rate, warm, lift, property_right_year, createtime, property, last_buy_time, house_use, house_limit, property_right_belong, pledge_info, supplement, house_info
            if house_id in flags:
                continue
                # print 'Notice!!!', url, house_id, title, subtitle, buyer_attention, buyer_see, xiaoqu_name, region, area, ring_road, subway, total, house_type, floor, bulid_area, house_structure, use_area, bulid_type, orientation, build_structure, fitment, ladder_rate, warm, lift, property_right_year, createtime, property, last_buy_time, house_use, house_limit, property_right_belong, pledge_info, supplement, house_info, date
            flags.add(house_id)

            tmp = (house_id, buyer_attention, buyer_see, total, date)
            datas.append(tmp)

            if len(datas) == 10:
                cursor.executemany(ins_sql, datas)
                datas = []
    if len(datas) > 0:
        cursor.executemany(ins_sql, datas)
    print 'ershoufang: Done', '~' * 50
    # 关闭游标连接
    cursor.close()
    # 关闭数据库连接
    conn.close()

if __name__ == "__main__":
    date = datetime.now().strftime('%Y%m%d')
    # date='20180430'
    print date
    start = time.time()
    if len(sys.argv) == 2:
        types = sys.argv[1]
    if types == 'ershoufang':
        # 爬下所有二手房的信息
        do_ershoufang_spider(u'朝阳', date)

        # 一段时间内只入库一次，该表包括在售房的所有基础信息
        read_ershoufang(date)

        # # 每天入库一次，更新在售房的总价和关注度
        # read_ershoufang_price(date)

    end = time.time()
    print "抓取{types}耗时：{diff}秒".format(types=types, diff=int(end - start))
