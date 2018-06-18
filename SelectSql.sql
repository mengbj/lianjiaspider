--几个维度查询语句的SQL 推荐
--根据每个人关注的点不一样可以调整查询条件

--1、二手房
select
total_score '总得分', fitment_score '装修得分', defang_price_score '单价得分', defang_score '得房率得分', huxing_score '户型得分', chuanghu_score '窗户得分', chaoxiang_score '朝向得分', defang_area '得房面积',
if(round(defang_rate)>0, concat(format(defang_rate,1),'%'),'0%') '得房率',
defang_price '得房单价',total '总价',bulid_area '房本面积', buyer_attention '关注量',xiaoqu_name '小区名称',
area,ring_road,createtime,subway,floor,url
from ershoufang
where date='20180410' and floor not like '顶%' and floor not like '地%' and floor not like '底%'
and ((lift='有' and floor not like "低%") or (lift='无' and floor like "低%"))
and property_right_year like '7%'
and property not like '一类%' and property not like '二类%' and property not like '限价%'
and house_use<>'公寓'
and round(bulid_area) >80
and round(total) between 400 and 530
and house_info like '%落地窗%'
and region in ('朝阳')
/* and title like '%急%' */
/* and area in ('北苑') */
and xiaoqu_name like "%北苑%"
/* and createtime between '2017-03-01' and '2018-03-27' */
order by /* round(buyer_attention,1)  */total_score desc,createtime desc

--2、小区
SELECT remark,
       url,
       build_age,
       service_price,
       avg_price,
       subway,
       substring_index(lnglat, ',', 1) lng,
       substring_index(lnglat, ',', -1) lat
FROM xiaoqu
WHERE date='20180307'
  AND region='朝阳'
  AND service_price<>'暂无信息'
  AND cast(avg_price AS signed)<60000
  AND subway<>'-'
  AND build_age LIKE '2%'
ORDER BY service_price DESC

--3、成交分布及议价比分布
SELECT hangout_time, num, chengjiao_price, guapai_price, (guapai_price-chengjiao_price),(guapai_price-chengjiao_price)/guapai_price
FROM
  (SELECT hangout_time,
          count(1) num,
          round(sum(done_price)/count(1),1) chengjiao_price,
          round(sum(hangout_price)/count(1),1) guapai_price
   FROM chengjiao
   WHERE date='20180315'
     AND hangout_time>'2012-01-01'
   GROUP BY hangout_time) a
WHERE abs((guapai_price-chengjiao_price)/guapai_price)<0.5


--4、挂牌走势
SELECT createtime "挂牌时间",
       sum(round(total,1)) "总价",
       sum(round(bulid_area,1)) '总平米数',
                                sum(round(total,1))/sum(round(bulid_area,1)) '均价'
FROM ershoufang
WHERE date='20180321'
  AND floor NOT LIKE '顶%'
  AND floor NOT LIKE '地%'
  AND floor NOT LIKE '底%'
  AND property_right_year LIKE '7%'
  AND property NOT LIKE '一类%'
  AND property NOT LIKE '限价%'
  AND property NOT LIKE '二类%'
  AND house_use<>'公寓'
  AND round(bulid_area) >85
  AND round(total) BETWEEN 350 AND 520
  AND region IN ('朝阳')
  AND createtime BETWEEN '2018-01-01' AND '2018-03-21'
  AND (house_type LIKE '%2%'
       OR house_type LIKE '%3%')
GROUP BY createtime