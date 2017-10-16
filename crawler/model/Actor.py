import time, re, urllib
from bs4 import BeautifulSoup


class FakeBrowser(urllib.FancyURLopener):
    version = 'Mozilla/5.0'


class Actor:

    fake_browser = FakeBrowser()

    def __init__(self, imdb_link):
        self.imdb_link = imdb_link
        self.soup = BeautifulSoup(self.fake_browser.open(self.imdb_link), 'html.parser')
        self.parse()

    def parse(self):
        self.name = self.get_full_name()
        self.roles = self.get_roles()
        self.mini_bio = self.get_mini_bio()
        self.birth_date = self.get_birth_date()
        self.birth_place = self.get_birth_place()
        self.known_for = self.get_known_for()
        
    def get_full_name(self):
        return self.soup.find(name='span', itemprop='name').string.strip()

    def get_mini_bio(self):
        mini_bio = self.soup.find(name='div', itemprop='description')
        mini_bio and mini_bio.find(attrs={'class': 'see-more'}).decompose()
        return mini_bio and mini_bio.get_text().strip()

    def get_roles(self):
        return map(lambda x: x.string.strip(), self.soup.find_all(name='span', itemprop='jobTitle'))

    def get_birth_date(self):
        date_string = self.soup.find(itemprop='birthDate')
        try:
            if date_string:
                return time.strptime(date_string['datetime'], '%Y-%m-%d')
            else:
                return None
        except ValueError:
            try:
                return time.strptime(date_string['datetime'], '%Y-%m')
            except ValueError:
                try:
                    return time.strptime(date_string['datetime'], '%Y')
                except ValueError:
                    return None
    
    def get_birth_place(self):
        birth_place = self.soup.find(id='name-born-info')
        if birth_place:
            return birth_place.find_all(name='a')[-1].string.strip()
        
    def get_known_for(self):
        known_for_movies = self.soup.find(id='knownfor')
        if known_for_movies:
            known_for_movies = known_for_movies.find_all(attrs={'class': 'knownfor-title'})
            return ', '.join(map(lambda x: x.get_text().strip().replace('\n', ' '), known_for_movies))
        return None

    def get_height(self):
        # This one for later
        pass

    def __repr__(self):
        return "<Actor('%s', '%s' \n )>" % (self.name, ', '.join(self.roles))
