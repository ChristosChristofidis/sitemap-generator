**Requirements:**

* Python 2.7.10

* BeautifulSoup 3.2.1




**Example:**

`python sitemap_generator.py --url 'http://google.com' --depth 2 --threads 10 --verbose` 

**Notes:**

* If you don't set a scan depth for sites like google, it will never stop running. 
* The sitemap shouldn't contain more than 50k urls or be larger than 50MB. Create a sitemap index if that's the case.



