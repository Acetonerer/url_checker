# checker/management/commands/check_urls.py

import json
import asyncio
import aiohttp
from urllib.parse import urlparse
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Проверка URL асинхронно и определение доступных HTTP-методов'

    def add_arguments(self, parser):
        parser.add_argument('urls', nargs='+', type=str, help='Список URL для проверки')

    def handle(self, *args, **kwargs):
        urls = kwargs['urls']
        result = {}

        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(self.process_urls(urls))

        for res in results:
            if res:
                result.update(res)

        self.stdout.write(json.dumps(result, indent=4))

    async def process_urls(self, urls):

        tasks = [self.process_url(url) for url in urls]

        return await asyncio.gather(*tasks)

    async def process_url(self, url):
        parsed_url = urlparse(url)

        """
        Проверка валидности URL
        """
        if not self.is_valid_url(parsed_url):
            # Выводим сообщение для невалидных строк
            self.stdout.write(f'Строка "{url}" не является ссылкой.')
            return None

        """
        Проверка на HTTP/HTTPS
        """
        if parsed_url.scheme not in ['http', 'https']:
            self.stdout.write(f'Ссылка "{url}" не является HTTP/HTTPS ссылкой.')
            return None

        """
        Проверка доступных HTTP методы
        """
        methods = await self.check_http_methods(url)
        if methods:
            return {url: methods}
        else:

            return {url: "Нет доступных методов или URL недоступен."}

    async def check_http_methods(self, url):
        """
        Проверка доступных HTTP-методов для заданного URL
        """
        available_methods = {}
        methods_to_check = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH']

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_method(session, method, url) for method in methods_to_check]
            responses = await asyncio.gather(*tasks)

            for method, status_code in responses:
                if status_code is not None:
                    available_methods[method] = status_code

        return available_methods if available_methods else None

    async def fetch_method(self, session, method, url):
        """
        Выполнение HTTP-запроса для заданного метода и URL
        """

        try:
            async with session.request(method, url) as response:

                if response.status != 405:
                    return method, response.status
        except aiohttp.ClientError:
            pass
        return method, None

    def is_valid_url(self, parsed_url):
        """
        Проверка валидности URL по наличию схемы и домена
        """
        return bool(parsed_url.scheme and parsed_url.netloc)
