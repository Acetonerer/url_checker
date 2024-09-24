import pytest
from django.core.management import call_command
from unittest.mock import patch
import json


@pytest.mark.django_db
def test_valid_http_url(mocker):
    """Проверяет, что приложение корректно обрабатывает
        валидный HTTP URL и возвращает статус-коды доступных методов.
    """
    mock_response = mocker.patch('aiohttp.ClientSession.request')
    mock_response.return_value.__aenter__.return_value.status = 200

    with patch('sys.stdout.write') as mock_stdout:
        call_command('check_urls', 'http://example.com')

    expected_output = {
        "http://example.com": {
            "GET": 200,
            "POST": 200,
            "PUT": 200,
            "DELETE": 200,
            "OPTIONS": 200,
            "HEAD": 200,
            "PATCH": 200
        }
    }
    mock_stdout.assert_called_once_with(json.dumps(expected_output, indent=4) + '\n')


@pytest.mark.django_db
def test_invalid_url():
    """Проверяет, что приложение корректно обрабатывает
    невалидную строку и выводит соответствующее сообщение.
    """
    with patch('sys.stdout.write') as mock_stdout:
        call_command('check_urls', 'невалидная строка')

    mock_stdout.assert_any_call('Строка "невалидная строка" не является ссылкой.\n')


@pytest.mark.django_db
def test_non_http_url():
    """Проверяет, что приложение корректно обрабатывает
    ссылку, не являющуюся HTTP/HTTPS, и выводит соответствующее сообщение.
    """
    with patch('sys.stdout.write') as mock_stdout:
        call_command('check_urls', 'ftp://example.com')

    mock_stdout.assert_any_call('Ссылка "ftp://example.com" не является HTTP/HTTPS ссылкой.\n')


@pytest.mark.django_db
def test_multiple_urls(mocker):
    """Проверяет, что приложение корректно обрабатывает
    несколько URL и выводит соответствующие сообщения
    для валидных и невалидных ссылок.
    """
    # Мокаем ответ для валидного URL
    mock_response = mocker.patch('aiohttp.ClientSession.request')
    mock_response.return_value.__aenter__.return_value.status = 200

    with patch('sys.stdout.write') as mock_stdout:
        call_command('check_urls', 'http://example.com', 'невалидная строка', 'ftp://example.com')

    expected_output = {
        "http://example.com": {
            "GET": 200,
            "POST": 200,
            "PUT": 200,
            "DELETE": 200,
            "OPTIONS": 200,
            "HEAD": 200,
            "PATCH": 200
        }
    }
    expected_output_json = json.dumps(expected_output, indent=4)

    # Проверяем, что были вызваны все ожидаемые сообщения
    output_calls = [call[0][0] for call in mock_stdout.call_args_list]

    # Проверяем наличие сообщения о невалидной строке
    assert 'Строка "невалидная строка" не является ссылкой.\n' in output_calls
    assert 'Ссылка "ftp://example.com" не является HTTP/HTTPS ссылкой.\n' in output_calls
    assert expected_output_json + '\n' in output_calls
    assert len(output_calls) == 3  # Убедитесь, что вызовов было ровно 3



