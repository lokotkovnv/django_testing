from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        '/',
        '/news/1/',
        '/auth/login/',
        '/auth/logout/',
        '/auth/signup/',
    )
)
def test_pages_availability(client, url, news):
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url_pattern',
    (
        '/edit_comment/{}/',
        '/delete_comment/{}/',
    ),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, comment_id_for_args, url_pattern, expected_status
):
    comment_id = comment_id_for_args[0]
    url = url_pattern.format(comment_id)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_pattern, args',
    (
        ('/edit_comment/{}/', pytest.lazy_fixture('comment_id_for_args')),
        ('/delete_comment/{}/', pytest.lazy_fixture('comment_id_for_args')),
    )
)
def test_redirect_for_anonymous_client(client, url_pattern, args):
    comment_id = args[0]

    login_url = '/auth/login/'
    url = url_pattern.format(comment_id)
    expected_url = f'{login_url}?next={url}'

    response = client.get(url)
    assertRedirects(response, expected_url)
