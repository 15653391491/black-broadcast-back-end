import logging

from django.utils.datastructures import MultiValueDictKeyError


def page_request(request_dict):
    """
    获取分页的两个信息
    :param request_dict:
    :return:
    """
    try:
        limit = request_dict["limit"]
        page = request_dict["page"]
        if type(limit) is list:
            limit = limit[0]
        if type(page) is list:
            page = page[0]
    except MultiValueDictKeyError:
        return (0, 0)
    return (limit, page)
