from django.core.paginator import Paginator


# Глобальная константа, определяющая количество последних записей.
COUNT_LAST_POSTS = 10


def my_paginator(request, posts):
    """Главная страница сайта"""
    paginator = Paginator(posts, COUNT_LAST_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
