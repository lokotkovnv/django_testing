from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, news_id_for_args, form_data
):
    url = reverse('news:detail', args=news_id_for_args)
    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment_count = Comment.objects.count()
    assert comment_count == 0


def test_user_can_create_comment(
    author_client, author, news, news_id_for_args, form_data
):
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(
        author_client, news_id_for_args, bad_words_data
):
    url = reverse('news:detail', args=news_id_for_args)
    response = author_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assertFormError(response, form='form', field='text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
        author_client, comment_id_for_args, url_to_comments
):
    url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.delete(url)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, url_to_comments)
    comment_count = Comment.objects.count()
    assert comment_count == 0


def test_user_cant_delete_comment_of_another_user(
        admin_client, comment_id_for_args
):
    url = reverse('news:delete', args=comment_id_for_args)
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_count = Comment.objects.count()
    assert comment_count == 1


def test_author_can_edit_comment(
        author_client,
        comment_id_for_args,
        form_data, comment,
        url_to_comments,
        news, author
):
    url = reverse('news:edit', args=comment_id_for_args)
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_edit_comment_of_another_user(
        admin_client,
        comment_id_for_args,
        form_data, comment,
        news,
        author
):
    comment_text = comment.text
    url = reverse('news:edit', args=comment_id_for_args)
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == comment_text
    assert comment.news == news
    assert comment.author == author
