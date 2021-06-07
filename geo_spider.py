# -*- coding: utf-8 -*-
import logging
from os import listdir
from os.path import join

import click
import scrapy
import jsonlines
from scrapy.exceptions import CloseSpider
from scrapy.crawler import CrawlerProcess
from geo_alchemy import PlatformParser, SampleParser, SeriesParser


logger = logging.getLogger('geo-spider')
modes = ['incremental', 'missed']
settings = {
    'USER_AGENT': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit'
        '/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    )
}


def read_crawled_file(crawled_file, parser):
    with jsonlines.open(crawled_file, mode='r') as reader:
        for data in reader:
            parser.parse_dict(data)


def read_crawled_dir(crawled_dir, parser):
    for crawled_file in listdir(crawled_dir):
        with jsonlines.open(join(crawled_dir, crawled_file), mode='r') as reader:
            for data in reader:
                parser.parse_dict(data)


class PlatformItem(scrapy.Item):
    accession = scrapy.Field()
    title = scrapy.Field()
    technology = scrapy.Field()
    distribution = scrapy.Field()
    organisms = scrapy.Field()
    manufacturer = scrapy.Field()
    manufacturer_protocol = scrapy.Field()
    description = scrapy.Field()
    columns = scrapy.Field()
    internal_data = scrapy.Field()
    release_date = scrapy.Field()
    last_update_date = scrapy.Field()
    submission_date = scrapy.Field()

    def __repr__(self):
        return 'PlatformItem<%s>' % self['accession']


class SampleItem(scrapy.Item):
    accession = scrapy.Field()
    title = scrapy.Field()
    type = scrapy.Field()
    channel_count = scrapy.Field()
    channels = scrapy.Field()
    hybridization_protocol = scrapy.Field()
    scan_protocol = scrapy.Field()
    description = scrapy.Field()
    data_processing = scrapy.Field()
    supplementary_data = scrapy.Field()
    columns = scrapy.Field()
    internal_data = scrapy.Field()
    release_date = scrapy.Field()
    last_update_date = scrapy.Field()
    submission_date = scrapy.Field()
    platform = scrapy.Field()

    def __repr__(self):
        return f'Sample<{self["accession"]}>'


class SeriesItem(scrapy.Item):
    accession = scrapy.Field()
    title = scrapy.Field()
    pmids = scrapy.Field()
    summary = scrapy.Field()
    overall_design = scrapy.Field()
    experiment_types = scrapy.Field()
    supplementary_data = scrapy.Field()
    release_date = scrapy.Field()
    last_update_date = scrapy.Field()
    submission_date = scrapy.Field()
    samples = scrapy.Field()

    def __repr__(self):
        return f'Series<{self["accession"]}>'


class PlatformSpider(scrapy.Spider):
    name = 'platforms'

    def __init__(self, mode='incremental', **kwargs):
        assert mode in modes
        self.mode = mode
        super(PlatformSpider, self).__init__(**kwargs)

    def start_requests(self):
        url = 'https://www.ncbi.nlm.nih.gov/geo/browse/?view=platforms&display=20&zsort=date'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for accession in response.xpath(
            '//table[@id="geo_data"]/tbody/tr/td[1]/a/text()'
        ).extract():
            if accession in PlatformParser.platforms:
                if self.mode == 'incremental':
                    raise CloseSpider('All platforms have been crawled.')
                else:
                    continue
            logger.info('New accession found %s', accession)
            miniml_url = f'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}&targ=self&form=xml&view=quick'
            yield scrapy.Request(miniml_url, callback=self.parse_platform)
        next_page = response.xpath('//div[@class="pager"]/span[@class="next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_platform(self, response):
        try:
            platform = PlatformParser.from_miniml(response.body).parse()
            yield PlatformItem(platform.to_dict())
        except Exception as exc:
            logger.error('Error occurred when parsing data from %s', response.url)
            logger.exception(exc)


class SampleSpider(scrapy.Spider):
    name = 'samples'

    def __init__(self, mode='incremental', **kwargs):
        assert mode in modes
        self.mode = mode
        super(SampleSpider, self).__init__(**kwargs)

    def start_requests(self):
        url = 'https://www.ncbi.nlm.nih.gov/geo/browse/?view=samples&display=20&zsort=date'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for accession in response.xpath(
            '//table[@id="geo_data"]/tbody/tr/td[1]/a/text()'
        ).extract():
            if accession in SampleParser.samples:
                if self.mode == 'incremental':
                    raise CloseSpider('All samples have been crawled.')
                else:
                    continue
            logger.info('New accession found %s', accession)
            miniml_url = f'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}&targ=self&form=xml&view=quick'
            yield scrapy.Request(miniml_url, callback=self.parse_sample)
        next_page = response.xpath('//div[@class="pager"]/span[@class="next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_sample(self, response):
        try:
            sample = SampleParser.from_miniml(response.body).parse()
            yield SampleItem(sample.to_dict())
        except Exception as exc:
            logger.error('Error occurred when parsing data from %s', response.url)
            logger.exception(exc)


class SeriesSpider(scrapy.Spider):
    name = 'series'

    def __init__(self, mode='incremental', **kwargs):
        assert mode in modes
        self.mode = mode
        super(SeriesSpider, self).__init__(**kwargs)

    def start_requests(self):
        url = 'https://www.ncbi.nlm.nih.gov/geo/browse/?view=series&display=20&zsort=date'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for accession in response.xpath(
            '//table[@id="geo_data"]/tbody/tr/td[1]/a/text()'
        ).extract():
            if accession in SeriesParser.series:
                if self.mode == 'incremental':
                    raise CloseSpider('All series have been crawled.')
                else:
                    continue
            logger.info('New accession found %s', accession)
            miniml_url = f'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={accession}&targ=self&form=xml&view=quick'
            yield scrapy.Request(miniml_url, callback=self.parse_series)
        next_page = response.xpath('//div[@class="pager"]/span[@class="next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_series(self, response):
        try:
            series = SeriesParser.from_miniml(response.body).parse()
            yield SeriesItem(series.to_dict())
        except Exception as exc:
            logger.error('Error occurred when parsing data from %s', response.url)
            logger.exception(exc)


@click.group()
@click.option(
    '-d', '--debug-mode', is_flag=True,
    help='enable debug mode'
)
@click.option(
    '-l', '--log-file', type=click.Path(exists=False),
    default='geo-spider.log', show_default=True, help='log file'
)
def geo_spider(debug_mode, log_file):
    """
    geo-spider
    """
    level = logging.DEBUG if debug_mode else logging.WARNING
    logging.basicConfig(level=level, filename=log_file)


@geo_spider.command(name='platforms')
@click.option(
    '-cf', '--crawled-file', required=False,
    type=click.Path(exists=True), help='crawled jsonlines file'
)
@click.option(
    '-cd', '--crawled-dir', required=False,
    type=click.Path(exists=True),
    help='crawled directory, a directory that contains all crawled jsonlines files.'
)
@click.option(
    '-m', '--mode', default='incremental', show_default=True,
    type=click.Choice(modes), help='crawling mode'
)
@click.option(
    '-o', '--outfile', required=False, show_default=True,
    default='platforms.jl', help='output jsonlines file'
)
def geo_spider_platforms(crawled_file, crawled_dir, mode, outfile):
    """
    crawl metadata of GEO platforms
    """
    try:
        # 1. read all crawled platform accessions
        if crawled_file:
            read_crawled_file(crawled_file, PlatformParser)
        if crawled_dir:
            read_crawled_dir(crawled_dir, PlatformParser)
        if PlatformParser.platforms:
            print('%s crawled platforms totally.' % len(PlatformParser.platforms))
        else:
            print('No crawled platforms provided.')

        # 2. crawl new platforms
        settings['FEEDS'] = {outfile: {'format': 'jsonlines', 'encoding': 'utf-8'}}
        process = CrawlerProcess(settings)
        process.crawl(PlatformSpider, mode=mode)
        process.start()
    except jsonlines.jsonlines.InvalidLineError as exc:
        logging.exception(exc)
        raise click.UsageError('Invalid jsonlines file.')
    except Exception as exc:
        logging.exception(exc)
        raise click.UsageError('Unknown error occurred, refer to log file for details.')


@geo_spider.command(name='samples')
@click.option(
    '-pcf', '--platform-crawled-file', required=False,
    type=click.Path(exists=True), help='platform crawled jsonlines file'
)
@click.option(
    '-pcd', '--platform-crawled-dir', required=False,
    type=click.Path(exists=True),
    help='platform crawled directory, a directory that contains all platform crawled jsonlines files.'
)
@click.option(
    '-cf', '--crawled-file', required=False,
    type=click.Path(exists=True), help='crawled jsonlines file'
)
@click.option(
    '-cd', '--crawled-dir', required=False,
    type=click.Path(exists=True),
    help='crawled directory, a directory that contains all crawled jsonlines files.'
)
@click.option(
    '-m', '--mode', default='incremental', show_default=True,
    type=click.Choice(modes), help='crawling mode'
)
@click.option(
    '-o', '--outfile', required=False, show_default=True,
    default='samples.jl', help='output jsonlines file'
)
def geo_spider_samples(platform_crawled_file, platform_crawled_dir, crawled_file, crawled_dir, mode, outfile):
    """crawl metadata of GEO samples"""
    try:
        # 1. read all crawled platform files
        if platform_crawled_file:
            read_crawled_file(platform_crawled_file, PlatformParser)
        if platform_crawled_dir:
            read_crawled_dir(platform_crawled_dir, PlatformParser)
        if PlatformParser.platforms:
            print('%s crawled platforms totally.' % len(PlatformParser.platforms))
        else:
            print('No crawled platform provided.')

        # 2. read all crawled sample files
        if crawled_file:
            read_crawled_file(crawled_file, SampleParser)
        if crawled_dir:
            read_crawled_dir(crawled_dir, SampleParser)
        if SampleParser.samples:
            print('%s crawled samples totally.' % len(SampleParser.samples))
        else:
            print('No crawled sample provided.')

        # 3. crawl new samples
        settings['FEEDS'] = {outfile: {'format': 'jsonlines', 'encoding': 'utf-8'}}
        process = CrawlerProcess(settings)
        process.crawl(SampleSpider, mode=mode)
        process.start()
    except jsonlines.jsonlines.InvalidLineError as exc:
        logging.exception(exc)
        raise click.UsageError('Invalid jsonlines file.')
    except Exception as exc:
        logging.exception(exc)
        raise click.UsageError('Unknown error occurred, refer to log file for details.')


@geo_spider.command(name='series')
@click.option(
    '-pcf', '--platform-crawled-file', required=False,
    type=click.Path(exists=True), help='platform crawled jsonlines file'
)
@click.option(
    '-pcd', '--platform-crawled-dir', required=False,
    type=click.Path(exists=True),
    help='platform crawled directory, a directory that contains all platform crawled jsonlines files.'
)
@click.option(
    '-scf', '--sample-crawled-file', required=False,
    type=click.Path(exists=True), help='sample crawled jsonlines file'
)
@click.option(
    '-scd', '--sample-crawled-dir', required=False,
    type=click.Path(exists=True),
    help='sample crawled directory, a directory that contains all sample crawled jsonlines files.'
)
@click.option(
    '-cf', '--crawled-file', required=False,
    type=click.Path(exists=True), help='crawled jsonlines file'
)
@click.option(
    '-cd', '--crawled-dir', required=False,
    type=click.Path(exists=True),
    help='crawled directory, a directory that contains all crawled jsonlines files.'
)
@click.option(
    '-m', '--mode', default='incremental', show_default=True,
    type=click.Choice(modes), help='crawling mode'
)
@click.option(
    '-o', '--outfile', required=False, show_default=True,
    default='samples.jl', help='output jsonlines file'
)
def geo_spider_series(
    platform_crawled_file, platform_crawled_dir,
    sample_crawled_file, sample_crawled_dir,
    crawled_file, crawled_dir, mode, outfile
):
    """crawl metadata of GEO samples"""
    try:
        # 1. read all crawled platform files
        if platform_crawled_file:
            read_crawled_file(platform_crawled_file, PlatformParser)
        if platform_crawled_dir:
            read_crawled_dir(platform_crawled_dir, PlatformParser)
        if PlatformParser.platforms:
            print('%s crawled platforms totally.' % len(PlatformParser.platforms))
        else:
            print('No crawled platform provided.')

        # 2. read all crawled sample files
        if sample_crawled_file:
            read_crawled_file(sample_crawled_file, SampleParser)
        if sample_crawled_dir:
            read_crawled_dir(sample_crawled_dir, SampleParser)
        if SampleParser.samples:
            print('%s crawled samples totally.' % len(SampleParser.samples))
        else:
            print('No crawled sample provided.')

        # 3. read all crawled series files
        if crawled_file:
            read_crawled_file(crawled_file, SeriesParser)
        if crawled_dir:
            read_crawled_dir(crawled_dir, SeriesParser)
        if SampleParser.samples:
            print('%s crawled series totally.' % len(SeriesParser.series))
        else:
            print('No crawled series provided.')

        # 3. crawl new series
        settings['FEEDS'] = {outfile: {'format': 'jsonlines', 'encoding': 'utf-8'}}
        process = CrawlerProcess(settings)
        process.crawl(SeriesSpider, mode=mode)
        process.start()
    except jsonlines.jsonlines.InvalidLineError as exc:
        logging.exception(exc)
        raise click.UsageError('Invalid jsonlines file.')
    except Exception as exc:
        logging.exception(exc)
        raise click.UsageError('Unknown error occurred, refer to log file for details.')


if __name__ == '__main__':
    geo_spider()
