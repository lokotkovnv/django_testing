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

    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']

    assert list(object_list) == list(sorted_set)


@pytest.mark.django_db
def test_comments_order(client, news_id_for_args, comment_set):
    sorted_comment_set = Comment.objects.all().order_by('created')

    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert 'news' in response.context
    news_object = response.context['news']
    comments_from_page = news_object.comment_set.all()

    assert list(comments_from_page) == list(sorted_comment_set)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news_id_for_args):
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.get(url)
    assert 'form' in response.context
