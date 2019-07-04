from django.shortcuts import render
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from scrapy.crawler import CrawlerProcess
from cricinfo_spider.cricinfo_spider.spiders.player_stats import StatsGuruSpider
from django.conf import settings
from urllib.parse import urlparse

import os


def index(request):
    context = {}
    return render(request, template_name='scrapper_app/index.html', context=context)


def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)
    except ValidationError:
        return False

    return True


def crawl(request):
    response = {'status': 'FAILED'}
    try:
        if request.method == 'POST':
            url = request.POST.get('url', None)  # take url comes from client. (From an input may be?)
            if not url:
                return JsonResponse({'error': 'Missing  args'})

            if not is_valid_url(url):
                return JsonResponse({'error': 'URL is invalid'})

            file_path = os.path.join(settings.BASE_DIR + '/output.csv')
            domain = urlparse(url).netloc
            process = CrawlerProcess()
            process.crawl(StatsGuruSpider, url=url, domain=domain)
            process.start()

            file = open(file_path, 'rb')
            res = HttpResponse(file, content_type='application/csv')
            res['Content-Disposition'] = "attachment; filename=%s.%s" % ('output', 'csv')
            file.close()
            # os.remove(file_path)

            return res
        else:
            return JsonResponse({'error': 'ONLY POST REQUEST !'})

    except Exception as ex:
        print("exception =============================== ", repr(ex))
        response['error'] = repr(ex)

    return JsonResponse(response)