# -*- coding:utf8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.db import transaction
from decimal import Decimal

from horizon.models import (model_to_dict,
                            BaseManager,
                            get_perfect_filter_params)

import json
import datetime
import os


MEDIA_PICTURE_PATH = settings.PICTURE_DIRS['web']['media']


class Media(models.Model):
    """
    媒体资源
    """
    title = models.CharField('资源标题', max_length=128, db_index=True)
    subtitle = models.CharField('资源副标题', max_length=128, null=True, blank=True)
    description = models.TextField('资源描述/介绍', null=True, blank=True)

    # 资源类型：10：电影 20：电视剧 30：综艺节目
    media_type = models.IntegerField('资源类型', default=10)
    # 题材类别  1：爱情 2：战争 3：校园 4：真人秀
    theme_type = models.IntegerField('题材类别', default=1)
    # 项目进度  1：筹备期 2：策划期 3：xxx
    progress = models.IntegerField('项目进度', default=1)

    # 模板类型 1：模板1  2：模板2
    template_type = models.IntegerField('展示页面模板类型', default=1)
    # # 资源概要展示类型：1：电影、剧集  2：综艺、活动
    # outline_type = models.IntegerField('资源概要展示类型', default=1)

    # 标签：数据格式为JSON字符串，如：['综艺', '植入', '片头']
    tags = models.CharField('资源标签', max_length=256)

    # 资源热度
    temperature = models.FloatField('热度')
    # 票房预测
    box_office_forecast = models.FloatField('票房预测')
    # 口碑预测
    public_praise_forecast = models.FloatField('口碑预测')

    # 资源属性：数据格式为JSON字符串，如：[1, 3, 5] （数字为属性ID）
    # attributes = models.CharField('资源属性', max_length=256, )

    # # 导演：数据格式为JSON字符串，如：['斯皮尔伯格', '冯小刚']
    # director = models.CharField('导演', max_length=256)
    # # 主演：数据格式为JSON字符串，如：['汤姆克鲁斯', '威尔史密斯', '皮尔斯布鲁斯南']
    # stars = models.CharField('主演', max_length=256)
    # # 演员：数据格式为JSON字符串，如：['王晓霞', '詹姆斯', '韦德']
    # actors = models.CharField('演员', max_length=256)
    # # 监制：数据格式为JSON字符串，如：['欧文']
    # producer = models.CharField('监制', max_length=256)
    # # 出品公司：数据格式为JSON字符串，如：['华文映像', '福星传媒']
    # production_company = models.CharField('出品公司', max_length=256)
    #
    # # 预计开机/录制时间
    # recorded_time = models.DateTimeField('开机时间')

    # 资源概述 数据格式为字典形式的JSON字符串，如：{"导演": ["冯小刚", "吴宇森"],
    #                                        "主演": ["成龙", "李连杰"],
    #                                        "出演": ["巩俐", "章子怡"], ......}
    media_outline = models.TextField('资源概述')

    # 预计上映/播出时间
    air_time = models.DateTimeField('播出时间')
    # # 预计播出平台：数据格式为JSON字符串，如：['一线卫视', '视频网络渠道']
    # play_platform = models.CharField('播出平台', max_length=256)

    # 运营标记 0: 未设定 1：热门
    mark = models.IntegerField('运营标记', default=0)

    picture = models.ImageField('媒体资源原始图片', max_length=200,
                                upload_to=MEDIA_PICTURE_PATH,
                                default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))
    picture_profile = models.ImageField('简介图片', max_length=200,
                                        upload_to=MEDIA_PICTURE_PATH,
                                        default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))
    picture_detail = models.ImageField('详情图片', max_length=200,
                                       upload_to=MEDIA_PICTURE_PATH,
                                       default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))
    # picture_profile = models.CharField('简介图片',
    #                                    max_length=200,
    #                                    default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))
    # picture_detail = models.CharField('详情图片',
    #                                   max_length=200,
    #                                   default=os.path.join(MEDIA_PICTURE_PATH, 'noImage.png'))
    # 资源状态：1：正常 非1：已删除
    status = models.IntegerField('资源状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_media'
        ordering = ['-updated']
        unique_together = ['title', 'subtitle', 'status']

    class AdminMeta:
        json_fields = ['tags', 'media_outline']

    def __unicode__(self):
        return self.title

    def get_perfect_tags(self, tag_ids):
        tag_details = []
        for tag_id in tag_ids:
            tag = ResourceTags.get_object(pk=tag_id)
            if isinstance(tag, Exception):
                continue
            tag_details.append(tag.name)
        return tag_details

    @property
    def perfect_detail(self):
        detail = model_to_dict(self)
        for key in detail.keys():
            if key in self.AdminMeta.json_fields:
                if key == 'tags':
                    tag_ids = json.loads(detail[key])
                    detail[key] = self.get_perfect_tags(tag_ids)
                else:
                    detail[key] = json.loads(detail[key])

        media_type_dict = getattr(self, '_media_type_dict', {})
        theme_type_dict = getattr(self, '_theme_type_dict', {})
        progress_dict = getattr(self, '_progress_dict', {})
        media_type_ins = media_type_dict.get(self.media_type)
        if not media_type_ins:
            media_type_ins = MediaType.get_object(pk=self.media_type)
            media_type_dict[self.media_type] = media_type_ins
            setattr(self, '_media_type_dict', media_type_dict)
        theme_type_ins = theme_type_dict.get(self.theme_type)
        if not theme_type_ins:
            theme_type_ins = ThemeType.get_object(pk=self.theme_type)
            theme_type_dict[self.theme_type] = theme_type_ins
            setattr(self, '_theme_type_dict', theme_type_dict)
        progress_ins = progress_dict.get(self.progress)
        if not progress_ins:
            progress_ins = ProjectProgress.get_object(pk=self.progress)
            progress_dict[self.progress] = progress_ins
            setattr(self, '_progress_dict', progress_dict)
        detail['media_type_name'] = getattr(media_type_ins, 'name', None)
        detail['theme_type_name'] = getattr(theme_type_ins, 'name', None)
        detail['progress_name'] = getattr(progress_ins, 'name', None)
        return detail

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def get_detail(cls, **kwargs):
        instance = cls.get_object(**kwargs)
        if isinstance(instance, Exception):
            return instance
        return instance.perfect_detail

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_details(cls, **kwargs):
        instances = cls.filter_objects(**kwargs)
        if isinstance(instances, Exception):
            return instances

        details = []
        for ins in instances:
            details.append(ins.perfect_detail)
        return details


class MediaConfigure(models.Model):
    """
    媒体资源属性配置
    """
    media_id = models.IntegerField('媒体资源ID')

    dimension_id = models.IntegerField('所属维度ID', db_index=True)
    attribute_id = models.IntegerField('所属属性ID')

    # 数据状态：1：正常，非1：已删除
    status = models.IntegerField('状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_media_configure'
        index_together = ['dimension_id', 'attribute_id']
        unique_together = ['media_id', 'attribute_id', 'status']

    def __unicode__(self):
        return '%s:%s:%s' % (self.media_id, self.dimension_id, self.attribute_id)

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e


class MediaType(models.Model):
    """
    资源类型
    """
    name = models.CharField('资源类型名称', max_length=64, db_index=True)
    sort_order = models.IntegerField('排序顺序', default=0)

    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_media_type'
        unique_together = ['name', 'status']
        ordering = ['-updated']

    def __unicode__(self):
        return '%s' % self.name

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            instances = cls.objects.filter(**kwargs)
        except Exception as e:
            return e
        # 排序
        sort_instances = sorted(instances, key=lambda x: x.sort_order)
        key = -1
        for index, item in enumerate(sort_instances):
            if item.sort_order != 0:
                break
            key = index
        if key == -1:
            return sort_instances
        else:
            new_sort_list = sort_instances[key + 1:]
            new_sort_list.extend(sort_instances[:key + 1])
            return new_sort_list


class ThemeType(models.Model):
    """
    题材类别
    """
    name = models.CharField('题材类别名称', max_length=64)
    media_type_id = models.IntegerField('所属资源类型ID', db_index=True)
    sort_order = models.IntegerField('排序顺序', default=0)

    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_theme_type'
        unique_together = ['name', 'media_type_id', 'status']
        ordering = ['media_type_id', '-updated']

    def __unicode__(self):
        return '%s' % self.name

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            instances = cls.objects.filter(**kwargs)
        except Exception as e:
            return e
        # 排序
        sort_instances = sorted(instances, key=lambda x: x.sort_order)
        key = -1
        for index, item in enumerate(sort_instances):
            if item.sort_order != 0:
                break
            key = index
        if key == -1:
            return sort_instances
        else:
            new_sort_list = sort_instances[key + 1:]
            new_sort_list.extend(sort_instances[:key + 1])
            return new_sort_list


class ProjectProgress(models.Model):
    """
    项目进度
    """
    name = models.CharField('项目进度名称', max_length=64, db_index=True)
    sort_order = models.IntegerField('排序顺序', default=0)

    # 数据状态 1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_project_progress'
        unique_together = ['name', 'status']

    def __unicode__(self):
        return '%s' % self.name

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            instances = cls.objects.filter(**kwargs)
        except Exception as e:
            return e
        # 排序
        sort_instances = sorted(instances, key=lambda x: x.sort_order)
        key = -1
        for index, item in enumerate(sort_instances):
            if item.sort_order != 0:
                break
            key = index
        if key == -1:
            return sort_instances
        else:
            new_sort_list = sort_instances[key + 1:]
            new_sort_list.extend(sort_instances[:key + 1])
            return new_sort_list


class ResourceTags(models.Model):
    """
    资源标签
    """
    name = models.CharField('标签名字', max_length=64, db_index=True)
    description = models.CharField('描述', max_length=256, null=True, blank=True)

    # 数据状态：1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)
    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_resource_tag'
        ordering = ['-updated']
        unique_together = ['name', 'status']

    def __unicode__(self):
        return self.name

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e


INFORMATION_FILE_PATH = settings.PICTURE_DIRS['web']['information']


class Information(models.Model):
    """
    资讯
    """
    title = models.CharField('标题', max_length=128, db_index=True)
    subtitle = models.CharField('副标题', max_length=128, null=True, blank=True)
    description = models.TextField('描述/介绍', null=True, blank=True)

    content = models.TextField('正文')

    # 标签：数据格式为JSON字符串，如：['综艺', '植入', '片头']
    tags = models.CharField('标签', max_length=256)
    # 浏览数
    read_count = models.IntegerField('浏览数', default=0)
    # 点赞数量
    like = models.IntegerField('点赞数量', default=0)
    # 数据状态：1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)

    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_information'

    def __unicode__(self):
        return self.title

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e


CASE_FILE_PATH = settings.PICTURE_DIRS['web']['case']


class Case(models.Model):
    """
    案例
    """
    title = models.CharField('标题', max_length=128, db_index=True)
    subtitle = models.CharField('副标题', max_length=128, null=True, blank=True)
    description = models.TextField('描述/介绍', null=True, blank=True)

    content = models.TextField('正文')

    # 标签：数据格式为JSON字符串，如：['综艺', '植入', '片头']
    tags = models.CharField('标签', max_length=256)
    # 浏览数
    read_count = models.IntegerField('浏览数', default=0)
    # 点赞数量
    like = models.IntegerField('点赞数量', default=0)
    # 数据状态：1：正常 非1：已删除
    status = models.IntegerField('数据状态', default=1)

    created = models.DateTimeField('创建时间', default=now)
    updated = models.DateTimeField('更新时间', auto_now=True)

    objects = BaseManager()

    class Meta:
        db_table = 'by_case'

    def __unicode__(self):
        return self.title

    @classmethod
    def get_object(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.get(**kwargs)
        except Exception as e:
            return e

    @classmethod
    def filter_objects(cls, **kwargs):
        kwargs = get_perfect_filter_params(cls, **kwargs)
        try:
            return cls.objects.filter(**kwargs)
        except Exception as e:
            return e
