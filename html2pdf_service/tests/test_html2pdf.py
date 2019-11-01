from unittest import mock

import pytest

import app


@pytest.fixture
def client():
    app.app.config['TESTING'] = True

    with app.app.test_client() as client:
        yield client


@mock.patch('app.pdfkit')
def test_call_shell_method(pdfkit, client):

    pdfkit.from_string.return_value = 'pdf-data'

    response = client.post('/html2pdf', data="<html></html>")

    assert response.status_code == 200
    assert response.data == b'pdf-data'
    pdfkit.from_string.assert_called_with(
        '<html></html>',
        output_path=False,
        options=mock.ANY,
        configuration=mock.ANY,
    )
