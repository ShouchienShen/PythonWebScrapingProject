# scrapy web scraping project
# WEBMD pain medications Spider
from scrapy import Spider, Request
from webmd.items import WebmdItem
import re

# define Spider
class WebmdSpider(Spider):
    name = 'webmd_spider'
    allowed_urls = ['https://www.webmd.com']
    # result url from a "search by condition" for chronic pain
    start_urls = ['https://www.webmd.com/drugs/2/condition-3090/chronic%20pain']

    # want the top 4 reviewed pain medications
    # get a list of all the urls for each drug's page
    # there are different names for the same drug reviewed...
    # so only want the first url for each unique drug
    # which can be differentiated by the number of reviews (same drugs have same number of reviews)
    def parse(self, response):
        drug_review_urls = response.xpath('//div/table/tbody/tr/td[4]')
        # return a nested list of the top 5 unique drugs' review page urls and the total number of reviews
        drug_list = [['test_url', '0']] # initial list item to compare first drug's number of reviews
        for review in drug_review_urls:
            num_reviews = review.xpath('./a/text()').extract()[0].split(' ')[0]
            if num_reviews != drug_list[-1][-1]:
                url = review.xpath('./a/@href').extract_first()
                # add 'https://www.webmd.com' since the extracted url doesn't have that
                url = 'https://www.webmd.com' + url
                drug_list.append([url, num_reviews])
            if len(drug_list) >= 8:
                del drug_list[0] # removes my initial list item
                del drug_list[3]
                break

        # direct spider to request the initial review page
        for list_item in drug_list:
            url = list_item[0]
            num_reviews = list_item[1]
            yield Request(url=url, meta={'url': url, 'num_reviews': num_reviews}, callback=self.parse_review_page)


    # construct list of urls for every review page
    def parse_review_page(self, response):
        num_reviews = int(response.meta['num_reviews'])
        # get the number of pages of reviews
        reviews_per_page = 5
        pages = num_reviews // reviews_per_page
        # Prepare url so that it returns reviews for all conditions and has pageIndex formatted:
        # 1) pageIndex={} (starts at 0)
        # 2) sortby=3
        # 3) conditionFilter=-1
        base_url = response.meta['url']+'&pageIndex={}&sortby=3&conditionFilter=-1'
        # list of all urls for every review page
        review_pages = [base_url.format(i) for i in range(0, pages)]

        # direct spider to request each review page
        for url in review_pages: #test first 2 pages
            yield Request(url=url, callback=self.parse_details)


    # extract all the details from a review page
    def parse_details(self, response):
        # xpath for all 5 user reviews per page
        reviews = response.xpath('//div[@class="userPost"]')
        # get the length (5 per page, except last page)
        num_reviews = len(reviews)
        # only need one "userPost": each one contains all the information for all reviews on the page
        reviews = reviews[0]

        # regex patterns for reviewer info text fields
        ageRegex = re.compile('13-18|19-24|25-34|35-44|45-54|55-64|65-74|75 or over')
        timeRegex = re.compile('less than 1 month|1 to 6 months|6 months to less than 1 year|1 to less than 2 years|2 to less than 5 years|5 to less than 10 years|10 years or more')
        statusRegex = re.compile('Patient|Caregiver')
        genderRegex = re.compile('Male|Female')
        # regex pattern for comment text field -- clean up extraneous characters
        commentRegex = re.compile('Comment:|Hide Full Comment|\r|\n|\t')

        # define the item
        item = WebmdItem()

        # cannot split xpath into different user reviews
        # must return list of 5 for each field of interest
        # and index them to get complete review info for one user
        for i in range(0, num_reviews):
            # much of the text that is returned for each field of interest is extraneous
            # thus, split functions are used to create a list of text from which info of interest can be extracted cleanly
            item['drug'] = response.xpath('//div[@class="tb_main"]/h1/text()').extract_first().split('- ')[1]
            item['condition'] = reviews.xpath('//div[@class="conditionInfo"]/text()').extract()[i].split(': ')[1]
            item['date'] = reviews.xpath('//div[@class="date"]/text()').extract()[i].split(' ')[0]
            # format date:
            # item['date'] = datetime.strptime(item['date'], '%m/%d/%Y %I:%M:%S %p')

            # complete text field of information about the reviewer
            reviewerInfo = reviews.xpath('//p[@class="reviewerInfo"]/text()').extract()[i]
            # find the relevant information with regex
            item['age'] = ageRegex.findall(reviewerInfo)
            item['gender'] = genderRegex.findall(reviewerInfo)
            item['treatment_length'] = timeRegex.findall(reviewerInfo)
            item['reviewer_status'] = statusRegex.findall(reviewerInfo)
            # the ratings for the ith review have an index of i+1
            item['effectiveness'] = reviews.xpath('//div[@id="ctnStars"]/div[1]/p[2]/span[@class="current-rating"]/text()').extract()[i+1].split(": ")[1]
            item['ease_of_use'] = reviews.xpath('//div[@id="ctnStars"]/div[2]/p[2]/span[@class="current-rating"]/text()').extract()[i+1].split(": ")[1]
            item['satisfaction'] = reviews.xpath('//div[@id="ctnStars"]/div[3]/p[2]/span[@class="current-rating"]/text()').extract()[i+1].split(": ")[1]

            # extract the all the text for the comments
            comments = [''.join(text.xpath('.//text()').extract()) for text in reviews.xpath('//p[3][@class="comment"]')]
            # create empty text field for reviews without comments
            item['comment'] = commentRegex.sub('', comments[i])

            yield item
