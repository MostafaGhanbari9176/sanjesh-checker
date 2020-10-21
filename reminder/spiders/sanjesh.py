import scrapy, smtplib, ssl


class SanjeshSpider(scrapy.Spider):
    name = 'sanjesh'
    allowed_domains = ['sanjesh.org']
    counter = 0
    _from = "reminder@mostafaghanbari.ir"
    _to = "godhelot1@gmail.com"
    last_message = ""

    def start_requests(self):
        print("start")
        self.send_mail(self.create_mail_message('starting local service', 'Hello, this is a log email'))
        yield scrapy.Request(url="http://sanjesh.org/", callback=self.parse, dont_filter=True, errback=self.err_back)

    def parse(self, response):
        self.counter = self.counter + 1
        if self.counter != 0 and self.counter % 12 == 0:
            self.send_mail(self.create_mail_message(f"Hourly reminder:{self.counter / 12}",
                                                    f"Hello, checking for {self.counter / 12} hours"))
        print(f"response number: {self.counter}")
        top_links = response.css('div .topLinks')
        for top in top_links:
            if 'ارشد' in top.xpath('./div[2]/h4/text()').get():
                img_new = top.xpath('./div[4]/ul/li[1]/a/img/@src').get()
                message = top.xpath('./div[4]/ul/li[1]/a/text()').get()
                if message == self.last_message:
                    break
                if img_new is None:
                    print("hey: noting")
                    self.logger.info(f"hey: noting")
                else:
                    self.last_message = message
                    print(f"hey: have news: {message}")
                    self.logger.info(f"hey: have news: {message}")
                    self.send_mail(self.create_mail_message('have news in sanjesh', message))
                break
        yield response.follow(url="http://sanjesh.org/", callback=self.parse, dont_filter=True, errback=self.err_back)

    def err_back(self, failure):
        self.logger.info(f"request failed, count:{self.counter}")
        yield scrapy.Request(url="http://sanjesh.org/", callback=self.parse, dont_filter=True, errback=self.err_back)

    def send_mail(self, message):
        try:
            ssl_context = ssl.create_default_context()
            print("create email instance")
            smtp = smtplib.SMTP_SSL('mail.mostafaghanbari.ir', 465, context=ssl_context)
            smtp.login(self._from, '*************************************************************')
            smtp.sendmail(self._from, self._to, message)
            smtp.close()
            print("success")
        except Exception as e:
            print(e)

    def create_mail_message(self, subject, body):
        return f"From: {self._from}\nTo: {self._to}\nSubject: {subject}\n\n{body}"
