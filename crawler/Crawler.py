import urllib
from bs4 import BeautifulSoup
from multiprocessing import Pool

from crawler.Repository import Repository
from crawler.model.Movie import Movie
from crawler.settings import ROOT_URL, URL_BOTTOM_100, URL_TOP_250, NUMBER_OF_THREADS

def retrieveAndSaveMovieData(url):
    movie = Movie(ROOT_URL + url)
    repository.saveMovie(movie)

def retrieveMovieList(url):
    print('Retriving movie Lists....')
    
    response = urllib.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    p = Pool(NUMBER_OF_THREADS)

    print('Fetching individual movie data...\nThis might take a while. Go get your coffee!')

    movie_url_list = set(map(lambda movie: movie['href'], soup.table.find_all('a')))
    map(retrieveAndSaveMovieData, movie_url_list)
    
    # p.close()
    # p.join() # Wait for the workers to die.
    # print('Voila!! It is all done now.')

if __name__ == '__main__':
    try:
        repository = Repository()
        repository.createSchema()
        retrieveMovieList(URL_TOP_250)
        retrieveMovieList(URL_BOTTOM_100)
    except IOError:
        print("Please check your internet connection.")