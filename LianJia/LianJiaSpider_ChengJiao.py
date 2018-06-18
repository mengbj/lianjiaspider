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


def chengjiao_spider(db_cj, url_page=u"http://bj.lianjia.com/chengjiao/pg1rs%E5%86%A0%E5%BA%AD%E5%9B%AD"):
    """
    爬取页面链接中的成交记录
    """
    try:
        req = urllib2.Request(url_page, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib2.urlopen(req, timeout=10).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text)
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        return
    except Exception, e:
        print e
        return
    cj_list = soup.findAll('div', {'class': 'info'})
    for i, cj in enumerate(cj_list):
        cj_title = cj.find('div', {'class': 'title'})
        # 房屋名
        print i, cj_title.find('a').string
        cj_address = cj.find_all('div', {'class': 'address'})
        for cj_a in cj_address:
            for key in cj_a.find('div', {'class': 'houseInfo'}).contents[1].split('|'):
                # 房屋朝向 是否带电梯
                print i, key
            for dD in cj_a.find('div', {'class': 'dealDate'}):
                # 成交日期
                print i, dD
            for tP in cj_a.find('div', {'class': 'totalPrice'}):
                # 成交总价
                print i, tP.string
        cj_flood = cj.find_all('div', {'class': 'flood'})
        for cj_f in cj_flood:
            # 楼层 建筑年代
            print i, cj_f.find('div', {'class': 'positionInfo'}).contents[1]
            for so in cj_f.find('div', {'class': 'source'}):
                # 成交中介
                print i, so
            for uP in cj_f.find('div', {'class': 'unitPrice'}):
                # 成交单价
                print i, uP.string
        cj_dI = cj.find('div', {'class': 'dealHouseInfo'})
        if type(cj_dI) == type(None):
            continue
        for cs in cj_dI.find_all('span'):
            if not cs.string:
                continue
            # 满五年 地铁房 学区房
            print i, cs.string
        cj_dC = cj.find('div', {'class': 'dealCycleeInfo'})
        if type(cj_dC) == type(None):
            continue
        for dC in cj_dC.find_all('span'):
            if not dC.string:
                continue
            # 挂牌价 挂牌周期
            print i, dC.string

    return ''


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


def chengjiao_spider1(base_file, url, date):
    """
        爬取页面链接中的成交记录
    """
    soup = get_soup(url)
    with open(base_file, 'a') as f:
        # f.write('\n'+'~~~~~~~~~' * 20)
        f.write("url: %s" % url)
        print '~~~~~~~~~' * 10
        print 'url: ', url
        house_id = str(url).split('/')[-1].split('.html')[0]
        f.write('    ' + "house_id: %s" % house_id)
        info_dict = defaultdict()
        info_dict['url'] = url
        try:
            sell_title = soup.find('div', {'class': 'house-title'}).find('div', {'class': 'wrapper'})
        except:
            sell_title = []
        titles = []
        for i, title_actinos in enumerate(sell_title):
            # 卖房的标题
            title = title_actinos.string
            if i < 2:
                titles.append(title)
        title = '/'.join(titles)
        if u'链家' not in title:
            f.write('\n')
            return
        print 'title: ', title
        f.write('    ' + 'title: %s' % title)

        # 小区名称 所在位置 看房时间
        try:
            done_price = soup.find('span', {'class': 'dealTotalPrice'}).find('i').string
        except:
            done_price = '-'
        print '成交总价: ', done_price
        f.write('    ' + '成交总价: %s' % done_price)

        # 核心数据
        try:
            infos = soup.find('div', {'class': 'msg'})
        except:
            infos = {}
        for info in infos:
            for i, io in enumerate(info.contents):
                if i == 0:
                    num = io.string
                else:
                    col = io.split('（')[0]
            # print col, [col], num, [num]
            print ': '.join([col, num])
            f.write('    ' + ': '.join([col, num]))

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
                        con = split_str(re.split(r'[\n\s]', base_content))
                        base_res = ': '.join([base_title, con])
                        print base_res
                        f.write('    ' + base_res)

        # 交易属性
        try:
            transactions = soup.find_all('div', {'class': 'transaction'})
        except:
            transactions = []
        for transaction in transactions:
            conts = transaction.find('div', {'class': 'content'}).find('ul')
            for i, cont in enumerate(conts.find_all('li')):

                titles_contents = cont.contents
                transaction_tmp = list()
                for j, titles_content in enumerate(titles_contents):
                    if j == 0:
                        col = titles_content.string
                    else:
                        # 过滤空格或换行符
                        con = split_str(re.split(r'[\n\s]', titles_content))
                print ': '.join([col, con])
                f.write('    ' + ': '.join([col, con]))

        f.write('    ' + 'date: %s' % date)
        f.write('\n')
        return ''


def do_xiaoqu_chengjiao_spider(date):
    """
    批量爬取小区成交记录
    """
    base_file = get_file('chengjiao', date)
    with open(base_file, 'wt') as f:
        f.write('')
    sel_sql = """select xiaoqu_name from xiaoqu  where date='{date}' group by xiaoqu_name
    """.format(date=date)

    try:
        print sel_sql
        cursor.execute(sel_sql)
        cursor.scroll(0, mode='absolute')
        results = cursor.fetchall()
    except:
        print 'select 执行有误'
    p = Pool(8)
    for r in results:
        xiaoqu_name = r[0]
        # print xiaoqu_name
        url = u"http://bj.lianjia.com/chengjiao/rs" + urllib2.quote(xiaoqu_name) + "/"
        print url
        soup = get_soup(url)
        total_pages = get_pages(soup)
        if total_pages == 0:
            continue
        print total_pages
        p.apply_async(sing_process_chengjiao, args=(base_file, xiaoqu_name, total_pages,))
    p.close()
    p.join()


def sing_process_chengjiao(base_file, xiaoqu_name, total_pages):
    for i in range(total_pages):
        url = u"http://bj.lianjia.com/chengjiao/pg%drs%s/" % (i + 1, urllib2.quote(xiaoqu_name))
        print url
        try:
            soup = get_soup(url)
            # 获取所有二手房的链接
            tmp = soup.find_all('div', {'class': 'info'})
        except:
            continue
        for urls in tmp:
            try:
                url = urls.find('div', {'class': 'title'}).find('a').get('href')
            except:
                continue
            if not url:
                continue
            print url, '~' * 10
            chengjiao_spider1(base_file, url, date)


def read_chengjiao(date):
    base_file = get_file('chengjiao', date)
    print base_file
    del_table('chengjiao', date)
    ins_sql = """insert into chengjiao
    (url, house_id, title, done_price, hangout_price, deal_cycle, adjust_price, buyer_see, buyer_attention, view_count, 
    house_type, floor, bulid_area, house_structure, use_area, bulid_type, orientation, bulided_age, fitment, 
    build_structure, warm, ladder_rate, property_right_year, lift, lianjia_id, property, hangout_time, house_use, 
    house_limit, house_right_belong, date) 
    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s) """

    datas = []
    info = []
    flags = set()

    with open(base_file, 'rt') as f:
        for tmp in f:
            break_flag = 0
            line = tmp.replace('\n', '')
            # print len(line.split('    '))
            eles = line.split('    ')
            # print eles
            print len(line.split('    '))
            if len(eles) == 31:
                info = []
                for i in range(31):
                    try:
                        ele = eles[i].split(': ')[1]
                        info.append(ele)
                    except:
                        break_flag = 1
            else:
                print len(line.split('    ')), '!' * 30, eles[1]
                continue

            if break_flag:
                continue

            info = escape_string(info)
            [url, house_id, title, done_price, hangout_price, deal_cycle, adjust_price, buyer_see, buyer_attention,
             view_count,
             house_type, floor, bulid_area, house_structure, use_area, bulid_type, orientation, bulided_age, fitment,
             build_structure, warm, ladder_rate, property_right_year, lift, lianjia_id, property, hangout_time,
             house_use,
             house_limit, house_right_belong, date] = info
            # print url, house_id, title, subtitle, buyer_attention, buyer_see, xiaoqu_name, total, house_type, floor, bulid_area,house_structure, use_area, bulid_type, orientation, build_structure, fitment, ladder_rate, warm, lift, property_right_year, createtime, property, last_buy_time, house_use, house_limit, property_right_belong, pledge_info, supplement, house_info
            if house_id in flags:
                continue
                # print 'Notice!!!', url, house_id, title, subtitle, buyer_attention, buyer_see, xiaoqu_name, region, area, ring_road, subway, total, house_type, floor, bulid_area, house_structure, use_area, bulid_type, orientation, build_structure, fitment, ladder_rate, warm, lift, property_right_year, createtime, property, last_buy_time, house_use, house_limit, property_right_belong, pledge_info, supplement, house_info, date
            flags.add(house_id)

            tmp = (
            url, house_id, title, done_price, hangout_price, deal_cycle, adjust_price, buyer_see, buyer_attention,
            view_count,
            house_type, floor, bulid_area, house_structure, use_area, bulid_type, orientation, bulided_age, fitment,
            build_structure, warm, ladder_rate, property_right_year, lift, lianjia_id, property, hangout_time,
            house_use,
            house_limit, house_right_belong, date)
            datas.append(tmp)

            if len(datas) == 10:
                cursor.executemany(ins_sql, datas)
                datas = []
    if len(datas) > 0:
        cursor.executemany(ins_sql, datas)
    print 'chengjiao: Done', '~' * 50
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

    if types == 'chengjiao':
        # 爬下所有小区里的成交信息
        do_xiaoqu_chengjiao_spider(date)
        read_chengjiao(date)
    end = time.time()
    print "抓取{types}耗时：{diff}秒".format(types=types, diff=int(end - start))
