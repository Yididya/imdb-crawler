import time, re, urllib
from bs4 import BeautifulSoup
from crawler.settings import ROOT_URL

class FakeBrowser(urllib.FancyURLopener):
    version = 'Mozilla/5.0'


class Movie:

    fake_browser = FakeBrowser()

    def __init__(self, imdb_link):
        self.ImdbLink = imdb_link
        self.Reviews = []

        response = self.fake_browser.open(imdb_link)
        html = response.read()
        self.soup = BeautifulSoup(html, 'html.parser')

        self.parse()

    def parse(self):
        

        self.Title = self.soup.title.string[:-14].strip()
        self.Rating = float(self.soup.find(itemprop="ratingValue").string.strip())

        dates = self.soup.find_all(name='meta', attrs={'itemprop': 'datePublished'})
        
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

        synopsis = self.soup.find(itemprop="description")
        self.Synopsis = re.sub(' +', ' ', synopsis.get_text().strip())

        directors = self.soup.find_all(itemprop="director")
        self.Directors = []

        for director in directors:
            self.Directors.append(unicode(director.find(itemprop='name').string))


        actor_cast_pairs = filter(lambda pair: len(pair) > 1,self.soup.find(attrs={'class':'cast_list'}).find_all('tr'))
        
        self.Actors = map(lambda pair: {
                                        'actor': unicode(pair.find(itemprop='actor').span.string.strip()), 
                                        'character' : unicode(re.sub('\s+', ' ', pair.find(attrs={'class':'character'}).get_text().split('/')[0].strip()))
                                    }, 
                                    actor_cast_pairs[1:])
        
        try: 
            self.Reviews = self.get_reviews()
        except Exception:
            pass
        
    def get_reviews(self):
        """
        Get reviews for the movie (Limited to only the first page of the review list: the most relevant ones)
        """

        reviews = []
        review_link_tag = self.soup.find('div', id='quicklinksMainSection').find_all('a')[2]
        if not 'quicklinkGray' in review_link_tag.get('class', []):
            review_soup = BeautifulSoup(self.fake_browser.open(ROOT_URL + review_link_tag['href']), 'html.parser')
            reviews = map(lambda x: { 'title': x.get_text(), 'detail': x.parent.find_next_sibling('p').get_text()} , review_soup.find_all('h2'))

        
        return reviews
    
    def get_genre(self):
        """
        Get list of genres for the movie comma separated
        """

        return list(map(lambda genre:genre.get_text(), self.soup.find_all(name='span', itemprop='genre')))

    def get_budget(self):
        """
        Returns the estimated budget of the movie in USD
        """
        
        budget = self.soup.find(text='Budget:')
        return budget.parent.next_sibling.strip() if budget else None

    def get_running_time(self):
        """
        Returns the running time of the movie
        """
        
        running_time = self.soup.find(name='time', itemprop='duration')
        return running_time.get_text().strip() if running_time else None
    
    def get_gross_income(self):
        business_url = self.ImdbLink + 'business'
        soup = BeautifulSoup(self.fake_browser.open(business_url), 'html.parser')

        gross_title = soup.find(name='h5', text='Gross')
        gross_usa = gross_title.find_next_sibling(string=re.compile('USA', re.IGNORECASE))
        gross_worldwide = gross_title.find_next_sibling(string=re.compile('worldwide', re.IGNORECASE))

        gross_usa = gross_usa.split()[0] if gross_usa else None
        gross_worldwide = gross_worldwide.split()[0] if gross_worldwide else None

        return gross_usa, gross_worldwide
    
    
    def __repr__(self):
        return "<Movie('%s', '%s', '%s')>" % (self.ImdbLink, self.Title, self.ReleaseDate)
