# -*- coding: utf-8 -*-
import re
# 区分客厅、卧室、阳台、厨房和卫生间， 补充：如有除以上的房间，加分
# 客厅和主卧记录详细信息
"""
1、是否有窗户：1.1 有窗户, 1.1.1 判定朝向： 南, 东, 西, 北
                        1.1.2 判定窗户类型：落地窗，普通窗
              1.2 无

2、得房率
3、得房单价
4、装修


"""
huxing_hold, defang_hold, defang_price_hold, fitment_hold = [0.3, 0.1, 0.4, 0.2]
# 户型
chaoxiang, chuanghu_type = [0.4, 0.6]
house_type_info = {
    '客厅': ['keting', 0.5],
    '卧室A': ['woshi', 0.3],
    '阳台': ['yangtai', 0.1],
    '厨房': ['chufang', 0.05],
    '卫生间': ['weishengjian', 0.05]
}

window_type_info = {
    '无': ['wuchuang', 0],
    '落': ['luodichuang', 100],
    '普': ['putongchuang', 70]
}

toward_type_info = {
    '南': ['south', 100],
    '东': ['east', 70],
    '西': ['west', 60],
    '北': ['north', 40],
    '无': ['notoward', 0]
}

# 得房率
defang_type_info = {
    '80, 100': 100,
    '75, 80': 70,
    '70, 75': 40,
    '0, 70': 10
}

# 得房单价
defang_price_info = {
    '4.0, 6.5': 100,
    '6.5, 7.0': 80,
    '7.0, 7.5': 60,
    '7.5, 8.0': 10
}

# 装修
fitment_info = {
    '精装': 100,
    '简装': 80,
    '其他': 60,
    '毛坯': 30
}

def get_score(house_info, area, total, fitment):
    house_infos = house_info.split('||')

    # 户型
    huxing_score, chuanghu_score, chaoxiang_score = huxing(house_infos)
    # print huxing_score, chuanghu_score, chaoxiang_score

    # 得房率
    defang_score, defang_area, defang_rate = defang(house_infos, area)
    # print defang_score,  defang_area

    # 得房单价
    defang_price_score, defang_price = unit_cost(total, house_infos)
    # print defang_price_score, defang_price

    # 装修
    fitment_score = get_fitment_score(fitment)
    # print fitment_score
    total_score = huxing_score + defang_score + defang_price_score + fitment_score
    print total_score, defang_score, huxing_score, chuanghu_score, chaoxiang_score, defang_area, defang_rate, defang_price_score, defang_price, fitment_score
    return total_score, defang_score, huxing_score, chuanghu_score, chaoxiang_score, defang_area, defang_rate, defang_price_score, defang_price, fitment_score


def huxing(house_infos):
    huxing_score_tmp = 0
    house_window_scores, house_toward_scores = 0, 0

    for houses in house_infos:
        if not houses:
            continue
        infos = houses.split(', ')
        if len(infos) != 4:
            continue
        # 户型得分
        house_window_score, house_toward_score = 0, 0
        house, area, towards, windows = infos
        for house_tmp in house_type_info.keys():
            # house_type_name = house_type_info[house_tmp][0]
            if house.startswith(house_tmp):
                house_type_rate = house_type_info[house_tmp][1]
                # 窗户类型得分
                for window_tmp in window_type_info.keys():
                    if windows.startswith(window_tmp):
                        window_type_num = window_type_info[window_tmp][1]
                        house_window_score = house_type_rate * window_type_num
                        house_window_scores += house_window_score
                        # print house, area, towards, windows
                        # print '窗户', huxing_hold, house_type_rate, window_type_num, house_window_score
                        break

                # 朝向得分
                for toward_tmp in toward_type_info.keys():
                    # print toward_tmp, '|', towards, toward_type_info[toward_tmp][1], '1'*20
                    if towards.startswith(toward_tmp):
                        toward_type_num = toward_type_info[toward_tmp][1]
                        # print toward_tmp, toward_type_num, '2'*20
                        house_toward_score = house_type_rate * toward_type_num
                        house_toward_scores += house_toward_score
                        # print '朝向', huxing_hold, house_type_rate, toward_type_num, house_toward_score
                        break
    chuanghu_score = chuanghu_type * house_window_scores
    chaoxiang_score = chaoxiang * house_toward_scores
    huxing_score_tmp = huxing_hold*(chuanghu_score + chaoxiang_score)

    return huxing_score_tmp, chuanghu_score, chaoxiang_score

def defang(house_infos, area):
    # 得房率得分
    defang_score = 0
    defang_area = defanglv(house_infos)
    # print "得房面积: ", defang_area
    try:
        area = float(re.match(r'[\d]*[\.]*[\d]*', area).group(0))
    except:
        area = 0
    # print [defang_area, area]
    defang_rate = round((defang_area/area * 100),2) if area > 0 else 0
    # print defang_rate
    for rangs in defang_type_info.keys():
        min_rate, max_rate = rangs.split(', ')
        if defang_rate >= int(min_rate) and defang_rate < int(max_rate):
            # print rangs
            defang_score = defang_hold * defang_type_info[rangs]
    return defang_score,defang_area, defang_rate

def defanglv(house_infos):
    num_area = 0
    hinfos = house_infos
    for hinfo in hinfos:
        try:
            hfo = float(hinfo.split('平米')[0].split(',')[1])
        except:
            hfo = 0
        num_area += hfo
    return num_area

def unit_cost(total, house_infos):
    defang_price_score = 0
    defang_area = defanglv(house_infos)
    defang_price = round(float(total)/defang_area, 2) if defang_area > 0 else 0
    for rangs in defang_price_info.keys():
        min_rate, max_rate = rangs.split(', ')
        if defang_price >= float(min_rate) and defang_price < float(max_rate):
            # print rangs
            defang_price_score = defang_price_hold * defang_price_info[rangs]
    return defang_price_score, defang_price

def get_fitment_score(fitment):
    fitment_score = 0
    for types in fitment_info.keys():
        if fitment == types:
            fitment_score = fitment_hold * fitment_info[types]
    return fitment_score

if __name__ == '__main__':
    house_info = "客厅, 43.14平米, 北, 落地窗||卧室A, 20.65平米, 东南, 落地窗||卧室B, 14.69平米, 东, 普通窗||厨房, 8.89平米, 北, 落地窗||卫生间, 4.82平米, 北, 普通窗||阳台A, 5.2平米, 东 北 西, 落地窗||阳台B, 1.98平米, 北 西, 落地窗||阳台C, 2.86平米, 南 东, 落地窗"
    area = "111.66"
    total="500"
    fitment = "其他"
    get_score(house_info, area, total, fitment)