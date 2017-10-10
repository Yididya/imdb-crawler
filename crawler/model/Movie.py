import time, re, urllib
from bs4 import BeautifulSoup
from crawler.settings import ROOT_URL

class FakeBrowser(urllib.FancyURLopener):
    version = 'Mozilla/5.0'


class Movie:
    def __init__(self, imdbLink = None):
        self.fake_browser = FakeBrowser()
        self.ImdbLink = imdbLink
        self.Reviews = []
        self.parse(imdbLink)

    def parse(self, url):
        response = urllib.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        self.Title = soup.title.string[:-14].strip()
        self.Rating = float(soup.find(itemprop="ratingValue").string.strip())

        dates = soup.find_all(name='meta', attrs={'itemprop': 'datePublished'})
        
        try:
            if len(dates):
                self.ReleaseDate = time.strptime(dates[0]['content'], '%Y-%m-%d')
            else:
                self.ReleaseDate = None
        except ValueError:
            try:
                self.ReleaseDate = time.strptime(dates[0]['content'], '%Y-%m')
            except ValueError:
                try:
                    self.ReleaseDate = time.strptime(dates[0]['content'], '%Y')
                except ValueError:
                    self.ReleaseDate = None

        synopsis = soup.find(itemprop="description")
        self.Synopsis = re.sub(' +', ' ', synopsis.get_text().strip())

        directors = soup.find_all(itemprop="director")
        self.Directors = []

        for director in directors:
            self.Directors.append(unicode(director.find(itemprop='name').string))


        actor_cast_pairs = filter(lambda pair: len(pair) > 1,soup.find(attrs={'class':'cast_list'}).find_all('tr'))
        
        self.Actors = map(lambda pair: {
                                        'actor': unicode(pair.find(itemprop='actor').span.string.strip()), 
                                        'character' : unicode(pair.find(attrs={'class':'character'}).get_text().split('/')[0].strip())
                                    }, 
                                    actor_cast_pairs[1:])
        
        try: 
            self.Reviews = self.get_reviews(soup)
        except Exception:
            pass
        
    def get_reviews(self, soup):
        """
        Get reviews for the movie (Limited to only the first page of the review list: the most relevant ones)
        """
        reviews = []
        review_link_tag = soup.find('div', id='quicklinksMainSection').find_all('a')[2]
        if not 'quicklinkGray' in review_link_tag.get('class', []):
            soup = BeautifulSoup(self.fake_browser.open(ROOT_URL + review_link_tag['href']), 'html.parser')
            reviews = map(lambda x: { 'title': x.get_text(), 'detail': x.parent.parent.find_next_sibling('p').get_text()} , soup.find(id='tn15content').find_all('h2'))

        
        return reviews

    def __repr__(self):
        return "<Movie('%s', '%s', '%s')>" % (self.ImdbLink, self.Title, self.ReleaseDate)
