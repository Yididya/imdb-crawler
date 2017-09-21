import time, re, urllib
from bs4 import BeautifulSoup

class Movie:
    def __init__(self, imdbLink = None):
        self.ImdbLink = imdbLink
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
        


    def __repr__(self):
        return "<Movie('%s', '%u', '%s')>" % (self.ImdbLink, self.Title, self.ReleaseDate)
