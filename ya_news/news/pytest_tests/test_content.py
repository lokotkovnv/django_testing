import pytest
from django.urls import reverse
from django.conf import settings

from news.models import News, Comment


@pytest.mark.django_db
def test_news_count(client, news_set):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_set):
    sorted_set = News.objects.all(
    ).order_by('-date')[:settings.NEWS_COUNT_ON_HOME_PAGE]
    sorted_set_dates = [news.date for news in sorted_set]

    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]

    assert all_dates == sorted_set_dates


@pytest.mark.django_db
def test_comments_order(client, news_id_for_args, comment_set):
    sorted_comment_set = Comment.objects.all().order_by('created')
    sorted_comment_set_dates = [
        comment.created for comment in sorted_comment_set
    ]

    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news_object = response.context['news']
    comments_from_page = news_object.comment_set.all()
    dates_from_page = [comment.created for comment in comments_from_page]

    assert dates_from_page == sorted_comment_set_dates


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.get(url)
    assert 'form' in response.context
