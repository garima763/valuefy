import requests
import json
import re
from util.Sentry import SentryLogger
from multiprocessing import Pool, Manager, Process


class get_urls:
    def __init__(self):
        self.url = "https://medium.com/"
        self.escape_extension = ["png", "xml", "jpg", "jpeg", "css", "io", "ico"]
        self.pool = Pool(processes=5)

    def group_by_owners(self, url, new_urls):
        try:
            json_data = ""
            try:
                if url.rsplit(".", 1)[1] not in self.escape_extension:
                    html_content = requests.get(url, verify=False)
                    data = html_content.content
                    json_data = json.dumps(data)
                else:
                    self.access_next_url(new_urls)
            except:
                new_url = filter(lambda x: x["url"] != url, new_urls)
                url = ""
            length = len(new_urls)
            visited_count = sum(1 for p in new_urls if p["is_visited"] == True)
            while length != visited_count:
                if json_data:
                    url, n = self.get_url(json_data)
                    json_data = json_data[n:]
                    if url:
                        if url.lower().replace("\\","") != self.url.lower():
                            new_urls.append({"url": url.replace("\\", ""), "is_visited": False})
                    else:
                        self.access_next_url(new_urls)
                else:
                    self.access_next_url(new_urls)
        except Exception as e:
            SentryLogger.log()
        self.access_next_url(new_urls)
        f = open("D:/urls", 'a+')
        f.write(new_urls)


    def get_url(self, page):
        regex = re.compile(r"<(?:a\b[^>]*>)")
        match = 0
        url = ""
        text = re.search(regex, page)
        if text is None:
            self.access_next_url(new_urls)
        else:
            if re.finditer(regex, page) is None:
                self.access_next_url(new_urls)
            else:
                matches = re.finditer(regex, page)
                if enumerate(matches) is not None:
                    for matchNum, match in enumerate(matches):
                        start_link = page[match.start(): match.end()]
                        start_link1 = start_link.find("href=")
                        if start_link1 == -1:
                            return None, 0
                        start_quote = start_link.find('"', start_link1)
                        end_quote = start_link.find('"', start_quote + 1)
                        url = start_link[start_quote + 1: end_quote]
                        return url, match.end()

    def access_next_url(self, new_urls):
        try:
            r=[]
            for ele in new_urls:
                if ele["url"] != self.url:
                    if not ele["is_visited"]:
                        temp_url = ele["url"].split(".")
                        if len(temp_url) > 1:
                            if temp_url[1] and temp_url[1] not in self.escape_extension:
                                ele["is_visited"] = True
                                r.append(Process(target=self.group_by_owners, args=(ele["url"], new_urls,)))
                                #pool.apply_async(self.group_by_owners, [ele["url"], new_urls])
                                #self.group_by_owners(ele["url"])
            for i in r:
                i.start()
            for i in r:
                i.join()
            # self.pool.close()
            # self.pool.join()
        except Exception as e:
            print e

pool = None
new_urls = []


def main():
    global pool
    pool = Pool(processes=5)

    test_manager = Manager()
    cr = get_urls()
    with test_manager:
        global new_urls
        new_urls = [{"url": "https://medium.com/", "is_visited": False}]
        cr.group_by_owners("https://medium.com/", new_urls)
        pool.close()
        pool.join()


if __name__ == '__main__':
    main()
