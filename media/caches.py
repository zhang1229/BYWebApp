# -*- coding:utf8 -*-
from __future__ import unicode_literals
import json
import datetime

from django.conf import settings
from horizon import redis
from django.utils.timezone import now

from media.models import (Media,
                          MediaType,
                          ThemeType,
                          ProjectProgress,
                          ResourceTags,
                          Information,
                          Case)

# 过期时间（单位：秒）
EXPIRES_24_HOURS = 24 * 60 * 60
EXPIRES_10_HOURS = 10 * 60 * 60


class MediaCache(object):
    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_SETTINGS['host'],
                                    port=settings.REDIS_SETTINGS['port'],
                                    db=settings.REDIS_SETTINGS['db_set']['web'])
        self.handle = redis.Redis(connection_pool=pool)

    # def get_dimension_id_key(self, dimension_id):
    #     return 'dimension_id:%s' % dimension_id
    #
    # def get_attribute_id_key(self, attribute_id):
    #     return 'attribute_id:%s' % attribute_id
    #
    # def get_tag_id_key(self, tag_id):
    #     return 'tag_id:%s' % tag_id

    def get_media_instance_id_key(self, media_id):
        return 'media:instance:id:%s' % media_id

    def get_media_id_key(self, media_id):
        return 'media:id:%s' % media_id

    def get_media_type_id_key(self, media_type_id):
        return 'media_type:id:%s' % media_type_id

    def get_theme_type_id_key(self, theme_type_id):
        return 'theme_type:id:%s' % theme_type_id

    def get_progress_id_key(self, progress_id):
        return 'progress:id:%s' % progress_id

    def get_resource_tag_id_key(self, resource_tag_id):
        return 'resource_tag:id:%s' % resource_tag_id

    def get_information_instance_id_key(self, information_id):
        return 'information:instance:id:%s' % information_id

    def get_information_id_key(self, information_id):
        return 'information:id:%s' % information_id

    def get_case_instance_id_key(self, case_id):
        return 'case:instance:id:%s' % case_id

    def get_case_id_key(self, case_id):
        return 'case:id:%s' % case_id

    def get_case_tags_dict_key(self):
        return 'case_tags_dict:tags'

    def get_media_tags_dict_key(self):
        return 'media_tags_dict:tags'

    def get_information_tags_dict_key(self):
        return 'information_tags_dict:tags'

    def get_media_sort_order_list_key(self):
        return 'media_sort_order_list:updated'

    def get_information_sort_order_list_key(self):
        return 'information_sort_order_list:updated'

    def get_case_sort_order_list_key(self):
        return 'case_sort_order_list:updated'

    def get_media_search_dict_title_tags_key(self):
        return 'media_search_dict:title_tags'

    def get_information_search_dict_title_tags_key(self):
        return 'information_search_dict:title_tags'

    def get_case_search_dict_title_tags_key(self):
        return 'case_search_dict:title_tags'

    def set_instance_to_cache(self, key, data):
        self.handle.set(key, data)
        self.handle.expire(key, EXPIRES_24_HOURS)

    def set_list_to_cache(self, key, *list_data):
        self.handle.rpush(key, *list_data)
        self.handle.expire(key, EXPIRES_24_HOURS)

    def get_instance_from_cache(self, key):
        return self.handle.get(key)

    def get_list_from_cache(self, key, start=0, end=-1):
        return self.handle.lrange(key, start, end)

    def get_perfect_data(self, key, model_function, **kwargs):
        data = self.get_instance_from_cache(key)
        if not data:
            data = model_function(**kwargs)
            if isinstance(data, Exception):
                return data
            self.set_instance_to_cache(key, data)
        return data

    def get_perfect_list_data(self, key, model_function, **kwargs):
        list_data = self.get_list_from_cache(key)
        if not list_data:
            list_data = model_function(**kwargs)
            if isinstance(list_data, Exception) or not list_data:
                return list_data
            self.set_list_to_cache(key, *list_data)
        return list_data

    # # 获取维度model对象
    # def get_dimension_by_id(self, dimension_id):
    #     key = self.get_dimension_id_key(dimension_id)
    #     return self.get_base_instance_by_key(dimension_id, key, Dimension)
    #
    # # 获取属性model对象
    # def get_attribute_by_id(self, attribute_id):
    #     key = self.get_attribute_id_key(attribute_id)
    #     return self.get_base_instance_by_key(attribute_id, key, Attribute)
    #
    # # 获取标签model对象
    # def get_tag_by_id(self, tag_id):
    #     key = self.get_tag_id_key(tag_id)
    #     return self.get_base_instance_by_key(tag_id, key, Tag)

    # 获取媒体资源Model对象
    def get_media_by_id(self, media_id):
        key = self.get_media_instance_id_key(media_id)
        kwargs = {'pk': media_id}
        return self.get_perfect_data(key, Media.get_object, **kwargs)

    # 获取媒体资源detail
    def get_media_detail_by_id(self, media_id):
        key = self.get_media_id_key(media_id)
        kwargs = {'pk': media_id}
        return self.get_perfect_data(key, Media.get_detail, **kwargs)

    # 获取媒体资源的标签为Key的列表
    def get_media_tags_dict(self):
        key = self.get_media_tags_dict_key()
        return self.get_perfect_data(key, Media.get_tags_key_dict)

    # 获取资源类型model对象
    def get_media_type_by_id(self, media_type_id):
        key = self.get_media_id_key(media_type_id)
        kwargs = {'pk': media_type_id}
        return self.get_perfect_data(key, MediaType.get_object, **kwargs)

    # 获取题材类别model对象
    def get_theme_type_by_id(self, theme_type_id):
        key = self.get_theme_type_id_key(theme_type_id)
        kwargs = {'pk': theme_type_id}
        return self.get_perfect_data(key, ThemeType.get_object, **kwargs)

    # 获取项目进度model对象
    def get_progress_by_id(self, progress_id):
        key = self.get_progress_id_key(progress_id)
        kwargs = {'pk': progress_id}
        return self.get_perfect_data(key, ProjectProgress.get_object, **kwargs)

    # 获取资源标签model对象
    def get_resource_tag_by_id(self, resource_tag_id):
        key = self.get_resource_tag_id_key(resource_tag_id)
        kwargs = {'pk': resource_tag_id}
        return self.get_perfect_data(key, ResourceTags.get_object, **kwargs)

    # 获取资讯Model对象
    def get_information_by_id(self, information_id):
        key = self.get_information_instance_id_key(information_id)
        kwargs = {'pk': information_id}
        return self.get_perfect_data(key, Information.get_object, **kwargs)

    # 获取资讯详情
    def get_information_detail_by_id(self, information_id):
        key = self.get_information_id_key(information_id)
        kwargs = {'pk': information_id}
        return self.get_perfect_data(key, Information.get_detail, **kwargs)

    # 获取资讯的标签为Key的列表
    def get_information_tags_dict(self):
        key = self.get_information_tags_dict_key()
        return self.get_perfect_data(key, Information.get_tags_key_dict)

    # 获取案例Model对象
    def get_case_by_id(self, case_id):
        key = self.get_case_instance_id_key(case_id)
        kwargs = {'pk': case_id}
        return self.get_perfect_data(key, Case.get_object, **kwargs)

    # 获取案例详情
    def get_case_detail_by_id(self, case_id):
        key = self.get_case_id_key(case_id)
        kwargs = {'pk': case_id}
        return self.get_perfect_data(key, Case.get_detail, **kwargs)

    # 获取案例的标签为Key的列表
    def get_case_tags_dict(self):
        key = self.get_case_tags_dict_key()
        return self.get_perfect_data(key, Case.get_tags_key_dict)

    # 获取媒体资源排序顺序列表
    def get_media_sort_order_list(self):
        key = self.get_media_sort_order_list_key()
        return self.get_perfect_data(key, Media.get_sort_order_list)

    # 获取媒体资源排序顺序列表
    def get_information_sort_order_list(self):
        key = self.get_information_sort_order_list_key()
        return self.get_perfect_data(key, Information.get_sort_order_list)

    # 获取媒体资源排序顺序列表
    def get_case_sort_order_list(self):
        key = self.get_case_sort_order_list_key()
        return self.get_perfect_data(key, Case.get_sort_order_list)

    # 获取媒体资源ID为Key，title和tags为Value的字典（搜索用）
    def get_media_search_dict(self):
        key = self.get_media_search_dict_title_tags_key()
        return self.get_perfect_data(key, Media.get_search_dict)

    # 获取资讯ID为Key，title和tags为Value的字典（搜索用）
    def get_information_search_dict(self):
        key = self.get_information_search_dict_title_tags_key()
        return self.get_perfect_data(key, Information.get_search_dict)

    # 获取案例ID为Key，title和tags为Value的字典（搜索用）
    def get_case_search_dict(self):
        key = self.get_case_search_dict_title_tags_key()
        return self.get_perfect_data(key, Case.get_search_dict)

