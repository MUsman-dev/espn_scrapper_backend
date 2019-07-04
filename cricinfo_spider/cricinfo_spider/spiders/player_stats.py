import scrapy
import re, csv
from cricinfo_spider.cricinfo_spider.items import CricinfoSpiderItem


class StatsGuruSpider(scrapy.Spider):
    name = 'statsguru'

    start_urls = [
        # 'http://stats.espncricinfo.com/ci/engine/player/253802.html?class=2;home_or_away=1;home_or_away=2;home_or_away=3;result=1;result=2;result=3;result=5;template=results;type=batting;view=dismissal_list'
    ]
    # if start_urls:
    #     player_id = str(start_urls[0].split('/')[6].split('.')[0])

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url')
        self.domain = kwargs.get('domain')
        self.start_urls = [self.url]
        self.allowed_domains = [self.domain]
        if self.start_urls:
            self.player_id = str(self.start_urls[0].split('/')[6].split('.')[0])
        self.outfile = open("output.csv", "w", newline="")
        self.writer = csv.writer(self.outfile)
        self.writer.writerow(['Player Name', 'How Out', 'Fielder', 'Bowler', 'Runs', 'Inns', 'Opposition', 'Ground', 'Date',
                         'Description', 'Balls', 'Minutes', '4s', '6s', 'SR'])
        super(StatsGuruSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        table = response.xpath('//div[@class="pnl650M"]//table[@class="engineTable"]//tbody/tr')
        i = 0
        for row in table:
            i += 1
            if i > 2:
                details = {
                        'how_out': row.xpath('td[1]//text()').extract() or [None],
                        'fielder': row.xpath('td[2]//text()').extract() or [None],
                        'bowler': row.xpath('td[3]//text()').extract() or [None],
                        'runs': row.xpath('td[4]//text()').extract() or [None],
                        'inns': row.xpath('td[5]//text()').extract() or [None],
                        'opposition': row.xpath('td[7]//text()').extract() or [None],
                        'ground': row.xpath('td[8]//text()').extract() or [None],
                        'start_date': row.xpath('td[9]//text()').extract() or [None],
                        'odi': row.xpath('td[10]//a/@href').extract(),
                }

                request = scrapy.Request("http://stats.espncricinfo.com"+str(details.get('odi')[0]), callback=self.parse_detail_page)
                request.meta['how_out'] = details.get('how_out')[0]
                request.meta['fielder'] = details.get('fielder')[0]
                request.meta['bowler'] = details.get('bowler')[0]
                request.meta['runs'] = details.get('runs')[0]
                request.meta['inns'] = details.get('inns')[0]
                request.meta['opposition'] = details.get('opposition')[1]
                request.meta['ground'] = details.get('ground')[0]
                request.meta['start_date'] = details.get('start_date')[0]
                request.meta['odi'] = details.get('odi')[0]
                yield request

    def parse_detail_page(self, response):
        batting_sessions = response.xpath('//div[@class="scorecard-section batsmen"]')
        for b_s in batting_sessions:
            try:
                flex_row = b_s.xpath('.//div[@class="flex-row"]')
                for row in flex_row:
                    player_url = row.xpath('.//div[@class="cell batsmen"]/a/@href').extract_first()
                    player_name = row.xpath('.//div[@class="cell batsmen"]//text()').extract()
                    stats = row.xpath('.//div[@class="cell runs"]//text()').extract()
                    discription = row.xpath('.//div[@class="commentary-content collapse"]//div[@class="content"]//text()').extract()
                    if player_url:
                        player_id_2 = re.findall("\d+", player_url)[0]
                        if self.player_id == player_id_2:
                            if 'SR' in stats and len(stats) > 6:
                                stats = stats[-6:]
                            elif len(stats) == 5:
                                stats.insert(2, 0)
                            cric_info = CricinfoSpiderItem()
                            cric_info['how_out'] = response.meta['how_out']
                            cric_info['fielder'] = response.meta['fielder']
                            cric_info['bowler'] = response.meta['bowler']
                            cric_info['runs'] = response.meta['runs']
                            cric_info['inns'] = response.meta['inns']
                            cric_info['opposition'] = response.meta['opposition']
                            cric_info['ground'] = response.meta['ground']
                            cric_info['start_date'] = response.meta['start_date']
                            cric_info['description'] = "".join(s for s in discription) if discription else ""
                            cric_info['name'] = player_name[1] if player_name[0].lower() == 'batsmen' else player_name[0]

                            cric_info['balls'] = stats[1]
                            cric_info['minutes'] = stats[2]
                            cric_info['fours'] = stats[3]
                            cric_info['sixes'] = stats[4]
                            cric_info['strike_rate'] = stats[5]

                            self.writer.writerow([cric_info['name'], cric_info['how_out'], cric_info['fielder'], cric_info['bowler'], cric_info['runs'], cric_info['inns'], cric_info['opposition']
                                                  ,cric_info['ground'], cric_info['start_date'], cric_info['description'], cric_info['balls'], cric_info['minutes'], cric_info['fours']
                                                  , cric_info['sixes'], cric_info['strike_rate']])
                            yield cric_info

            except Exception as ex:
                print(repr(ex))
                continue