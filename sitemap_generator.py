import urllib2
from pprint import pprint

from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
from multiprocessing.dummy import Pool as ThreadPool
import re
from tqdm import tqdm

HISTORY = set()


class UrlString(str):
    def _split(self):
        import urllib2

        return urllib2.splittype(self)[0], \
               urllib2.splithost(urllib2.splittype(self)[1])[0], \
               urllib2.splithost(urllib2.splittype(self)[1])[1]


regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def _page_source(url):
    return urllib2.urlopen(url).read()


def _valid(u, regex=regex):
    if regex.match(u):
        return True
    return False


def _get_all_hrefs(url, page_source):
    hrefs = []
    try:
        soup = BeautifulSoup(page_source)
        results = soup.findAll('a', href=True)
        for a in results:
            href = a.get('href').encode('utf8')
            if not href.startswith('http'):
                href = urljoin(url, href)
            hrefs.append(href)
        return hrefs
    except:
        return []


def scan(target):
    results = set()

    try:
        if target not in HISTORY:
            HISTORY.add(target)
            url = UrlString(target)
            hrefs = _get_all_hrefs(url, _page_source(url))

            for link in hrefs:
                if _valid(link):

                    s1 = UrlString(link)._split()[0]
                    s2 = '://' + UrlString(link)._split()[1]

                    if target.startswith(s1 + s2):
                        results.add(link)

            return results
    except:
        pass
    return set()


def bulk_scan(list_of_urls, threads=4):
    results = set()
    pool = ThreadPool(threads)
    temp = pool.map(scan, list_of_urls)
    pool.close()
    pool.join()

    for i in temp:
        results = results.union(i)
    return results


def generate_sitemap(list_of_urls):
    import xml.etree.cElementTree as ET

    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for url in list_of_urls:
        doc = ET.SubElement(root, "url")

        ET.SubElement(doc, "loc").text = url

    tree = ET.ElementTree(root)

    tree.write("sitemap.xml", encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url",
                      help="Specify the url to generate the sitemap from.")
    parser.add_option("-d", "--depth", dest="depth", default='inf',
                      help="Specify a maximum depth.")
    parser.add_option("-t", "--threads", dest="threads", default=4,
                      help="Specify a number of threads to be used.")

    parser.add_option('-v', '--verbose', action='store_true')

    (options, args) = parser.parse_args()

    results = scan(options.url)
    print "=================="
    print "No of Links : ", len(results), '\r'
    print "Level : ", 0, '\r'
    print "=================="
    print 'Going into level ->', 1

    level = 1
    previews_length = 0

    while level <= float(options.depth):

        temp = bulk_scan(list_of_urls=results, threads=int(options.threads))
        results = results.union(temp)
        current_length = len(results)

        if options.verbose:
            pprint(results)
        if current_length == previews_length:
            print 'There is no level', level
            break

        print "=================="
        print "No of Links : ", current_length, '\r'
        print "Level : ", level, '\r'
        print "=================="

        previews_length = current_length
        level += 1
        print 'Going into level ->', level

    generate_sitemap(results)

    print "sitemap.xml generated and saved to current directory."
