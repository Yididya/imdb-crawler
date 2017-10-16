import time, re, urllib
from bs4 import BeautifulSoup
from crawler.settings import ROOT_URL
from .Actor import Actor

class FakeBrowser(urllib.FancyURLopener):
    version = 'Mozilla/5.0'


class Movie:

    fake_browser = FakeBrowser()

    def __init__(self, imdb_link):
        self.imdb_link = imdb_link
        self.reviews = []

        response = self.fake_browser.open(imdb_link)
        html = response.read()
        print('Parsing movie page %s' % imdb_link) #TBR        
        self.soup = BeautifulSoup(html, 'html.parser')
        self.parse()

    def parse(self):
        

        self.title = self.soup.title.string[:-14].strip()
        self.rating = float(self.soup.find(itemprop="ratingValue").string.strip())

        dates = self.soup.find_all(name='meta', attrs={'itemprop': 'datePublished'})
        self.release_date = self.parse_date(dates)

        synopsis = self.soup.find(itemprop="description")
        self.synopsis = re.sub(' +', ' ', synopsis.get_text().strip())

        directors = self.soup.find_all(itemprop="director")
        self.directors = []

        for director in directors:
            self.directors.append(unicode(director.find(itemprop='name').string))


        actor_cast_pairs = filter(lambda pair: len(pair) > 1,self.soup.find(attrs={'class':'cast_list'}).find_all('tr'))
        print('Getting actor character pairs for %s ...' % self.title)
        self.actor_character_pairs = map(lambda pair: {
                                        # 'actor_imdb_link': ROOT_URL + pair.find(itemtype="http://schema.org/Person").find('a')['href'],
                                        'actor': Actor(ROOT_URL + pair.find(itemtype="http://schema.org/Person").find('a')['href']), 
                                        'character' : unicode(re.sub('\s+', ' ', pair.find(attrs={'class':'character'}).get_text().split('/')[0].strip()))
                                    }, 
                                    actor_cast_pairs[1:])

        
        try:
            print('Getting reviews for %s ...' % self.title)
            self.reviews = self.get_reviews()
        except:
            pass # TODO:// i dont know what
        
        
        self.gross_usa, self.gross_worldwide = self.get_gross_income()
        self.budget = self.get_budget()
        self.running_time = self.get_running_time()
        self.genre = self.get_genre()

    def get_reviews(self):
        """
        Get reviews for the movie (Limited to only the first page of the review list: the most relevant ones)
        """
        reviews = []
        review_link_tag = self.soup.find('div', id='quicklinksMainSection').find_all('a')[2]
        if not 'quicklinkGray' in review_link_tag.get('class', []):
            review_soup = BeautifulSoup(self.fake_browser.open(ROOT_URL + review_link_tag['href']), 'html.parser')
            # import ipdb; ipdb.set_trace()
            # reviews = map(lambda x: { 'title': x.get_text().encode('utf-8'), 'detail': x.parent.find_next_sibling('p') and x.parent.find_next_sibling('p').get_text().encode('utf-8')} , review_soup.find_all('h2'))
            reviews = map(lambda x: { 'title': x.get_text(), 'detail': x.parent.parent.find_next_sibling('p').get_text()} , review_soup.find_all('h2'))
            
        
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
        print('Getting gross income...')
        business_url = self.imdb_link + 'business'
        soup = BeautifulSoup(self.fake_browser.open(business_url), 'html.parser')

        gross_title = soup.find(name='h5', text='Gross')
        gross_usa = gross_title and gross_title.find_next_sibling(string=re.compile('USA', re.IGNORECASE))
        gross_worldwide = gross_title and gross_title.find_next_sibling(string=re.compile('worldwide', re.IGNORECASE))

        gross_usa = gross_usa.split()[0] if gross_usa else None
        gross_worldwide = gross_worldwide.split()[0] if gross_worldwide else None

        return gross_usa, gross_worldwide
    
    def parse_date(self, dates):
        try:
            if len(dates):
                return time.strptime(dates[0]['content'], '%Y-%m-%d')
            else:
                return None
        except ValueError:
            try:
                return time.strptime(dates[0]['content'], '%Y-%m')
            except ValueError:
                try:
                    return time.strptime(dates[0]['content'], '%Y')
                except ValueError:
                    return None
    
    def create_actors(self, actor_imdb_links):
        pass
    def __repr__(self):
        return "<Movie('%s', '%s', '%s')>" % (self.imdb_link, self.title, self.release_date)
