--建表语句的SQL

CREATE TABLE `ershoufang` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(200) DEFAULT NULL COMMENT '链接',
  `house_id` varchar(50) DEFAULT NULL COMMENT '房屋ID',
  `title` varchar(300) DEFAULT NULL COMMENT '主标题',
  `subtitle` varchar(300) DEFAULT NULL COMMENT '副标题',
  `buyer_attention` varchar(5) DEFAULT NULL COMMENT '关注房源',
  `buyer_see` varchar(5) DEFAULT NULL COMMENT '预约看房',
  `xiaoqu_name` varchar(50) DEFAULT NULL COMMENT '小区名称',
  `region` varchar(50) DEFAULT NULL COMMENT '区域',
  `area` varchar(50) DEFAULT NULL COMMENT '片区',
  `ring_road` varchar(50) DEFAULT NULL COMMENT '环路，如5环',
  `subway` varchar(100) DEFAULT NULL COMMENT '地铁',
  `total` varchar(10) DEFAULT NULL COMMENT '总价:万',
  `house_type` varchar(50) DEFAULT NULL COMMENT '房屋户型',
  `floor` varchar(50) DEFAULT NULL COMMENT '所在楼层',
  `bulid_area` varchar(10) DEFAULT NULL COMMENT '建筑面积:平米',
  `house_structure` varchar(50) DEFAULT NULL COMMENT '户型结构',
  `use_area` varchar(10) DEFAULT NULL COMMENT '套内面积:平米',
  `bulid_type` varchar(50) DEFAULT NULL COMMENT '建筑类型',
  `orientation` varchar(50) DEFAULT NULL COMMENT '房屋朝向',
  `build_structure` varchar(50) DEFAULT NULL COMMENT '建筑结构',
  `fitment` varchar(50) DEFAULT NULL COMMENT '装修情况',
  `ladder_rate` varchar(50) DEFAULT NULL COMMENT '梯户比例',
  `warm` varchar(50) DEFAULT NULL COMMENT '供暖方式',
  `lift` varchar(50) DEFAULT NULL COMMENT '配备电梯',
  `property_right_year` varchar(50) DEFAULT NULL COMMENT '产权年限',
  `createtime` varchar(50) DEFAULT NULL COMMENT '挂牌时间',
  `property` varchar(50) DEFAULT NULL COMMENT '交易权属',
  `last_buy_time` varchar(50) DEFAULT NULL COMMENT '上次交易',
  `house_use` varchar(50) DEFAULT NULL COMMENT '房屋用途',
  `house_limit` varchar(50) DEFAULT NULL COMMENT '房屋年限',
  `property_right_belong` varchar(50) DEFAULT NULL COMMENT '产权所属',
  `pledge_info` varchar(50) DEFAULT NULL COMMENT '抵押信息',
  `supplement` varchar(50) DEFAULT NULL COMMENT '房本备件',
  `house_info` varchar(800) DEFAULT NULL COMMENT '房屋详细信息',
  `remark` varchar(100) DEFAULT NULL COMMENT '备注',
  `defang_area` varchar(10) DEFAULT NULL COMMENT '得房面积总和',
  `defang_rate` varchar(5) DEFAULT NULL COMMENT '得房率',
  `defang_price` varchar(5) DEFAULT NULL COMMENT '得房单价',
  `chaoxiang_score` varchar(5) DEFAULT NULL COMMENT '朝向得分',
  `chuanghu_score` varchar(5) DEFAULT NULL COMMENT '窗户类型得分',
  `huxing_score` varchar(5) DEFAULT NULL COMMENT '户型(朝向+窗户)总得分',
  `defang_score` varchar(5) DEFAULT NULL COMMENT '得房率得分',
  `defang_price_score` varchar(5) DEFAULT NULL COMMENT '得房单价得分',
  `fitment_score` varchar(5) DEFAULT NULL COMMENT '装修分数',
  `total_score` varchar(5) DEFAULT NULL COMMENT '总分',
  `date` varchar(20) DEFAULT NULL COMMENT '日期',
  `ctime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `utime` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `house_id` (`house_id`,`date`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8



CREATE TABLE `chengjiao` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(200) DEFAULT NULL COMMENT '链接',
  `house_id` varchar(50) DEFAULT NULL COMMENT '房屋ID',
  `title` varchar(300) DEFAULT NULL COMMENT '标题',
  `done_price` varchar(300) DEFAULT NULL COMMENT '成交总价（万）',
  `hangout_price` varchar(300) DEFAULT NULL COMMENT '挂牌价格（万）',
  `deal_cycle` varchar(50) DEFAULT NULL COMMENT '成交周期（天）',
  `adjust_price` varchar(50) DEFAULT NULL COMMENT '调价（次）',
  `buyer_see` varchar(5) DEFAULT NULL COMMENT '带看（次）',
  `buyer_attention` varchar(5) DEFAULT NULL COMMENT '关注（人）',
  `view_count` varchar(50) DEFAULT NULL COMMENT '浏览（次）',
  `house_type` varchar(50) DEFAULT NULL COMMENT '房屋户型',
  `floor` varchar(50) DEFAULT NULL COMMENT '所在楼层',
  `bulid_area` varchar(10) DEFAULT NULL COMMENT '建筑面积:平米',
  `house_structure` varchar(50) DEFAULT NULL COMMENT '户型结构',
  `use_area` varchar(10) DEFAULT NULL COMMENT '套内面积:平米',
  `bulid_type` varchar(50) DEFAULT NULL COMMENT '建筑类型',
  `orientation` varchar(50) DEFAULT NULL COMMENT '房屋朝向',
  `bulided_age` varchar(50) DEFAULT NULL COMMENT '建成年代',
  `fitment` varchar(50) DEFAULT NULL COMMENT '装修情况',
  `build_structure` varchar(50) DEFAULT NULL COMMENT '建筑结构',
  `warm` varchar(50) DEFAULT NULL COMMENT '供暖方式',
  `ladder_rate` varchar(50) DEFAULT NULL COMMENT '梯户比例',
  `property_right_year` varchar(50) DEFAULT NULL COMMENT '产权年限',
  `lift` varchar(50) DEFAULT NULL COMMENT '配备电梯',
  `lianjia_id` varchar(50) DEFAULT NULL COMMENT '链家编号',
  `property` varchar(50) DEFAULT NULL COMMENT '交易权属',
  `hangout_time` varchar(50) DEFAULT NULL COMMENT '挂牌时间',
  `house_use` varchar(50) DEFAULT NULL COMMENT '房屋用途',
  `house_limit` varchar(50) DEFAULT NULL COMMENT '房屋年限',
  `house_right_belong` varchar(50) DEFAULT NULL COMMENT '房屋所属',
  `date` varchar(20) DEFAULT NULL COMMENT '日期',
  `ctime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `utime` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `house_id` (`house_id`,`date`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8



CREATE TABLE `xiaoqu` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(200) DEFAULT NULL COMMENT '链接',
  `xiaoqu_id` varchar(50) DEFAULT NULL COMMENT '小区ID',
  `xiaoqu_name` varchar(100) DEFAULT NULL COMMENT '小区名称',
  `build_age` varchar(50) DEFAULT NULL COMMENT '建筑年代',
  `bulid_type` varchar(50) DEFAULT NULL COMMENT '建筑类型',
  `service_price` varchar(50) DEFAULT NULL COMMENT '物业费用',
  `service_company` varchar(100) DEFAULT NULL COMMENT '物业公司',
  `developers` varchar(100) DEFAULT NULL COMMENT '开发商',
  `bulid_total` varchar(50) DEFAULT NULL COMMENT '楼栋总数',
  `house_total` varchar(50) DEFAULT NULL COMMENT '房屋总数',
  `near_zhongjie` varchar(100) DEFAULT NULL COMMENT '附近门店',
  `lnglat` varchar(50) DEFAULT NULL COMMENT '门店坐标',
  `avg_price` varchar(20) DEFAULT NULL COMMENT '小区均价',
  `refer_month` varchar(20) DEFAULT NULL COMMENT '均价参考月份',
  `house_type_total` varchar(50) DEFAULT NULL COMMENT '总户型数',
  `day30_done` varchar(10) DEFAULT NULL COMMENT '30天成交套数',
  `rent_num` varchar(10) DEFAULT NULL COMMENT '出租套数',
  `subway` varchar(100) DEFAULT NULL COMMENT '地铁',
  `date` varchar(20) DEFAULT NULL COMMENT '日期',
  `region` varchar(50) DEFAULT NULL COMMENT '区域',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  `ctime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `utime` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `xiaoqu_id` (`xiaoqu_id`,`date`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8