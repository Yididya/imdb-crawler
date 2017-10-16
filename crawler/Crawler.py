import urllib, re, pickle
from bs4 import BeautifulSoup
from multiprocessing import Pool

from crawler.Repository import Repository
from crawler.model.Movie import Movie
from crawler.settings import ROOT_URL, URL_BOTTOM_100, URL_TOP_250, NUMBER_OF_THREADS


def retrieve_and_save_movie(url):
    movie = Movie(ROOT_URL + url)
    repository.save_movie(movie)


def retrieve_movie_list(retry_index=0):
    print('Retriving movie Lists....')

    response_top = urllib.urlopen(URL_TOP_250)
    response_bottom = urllib.urlopen(URL_BOTTOM_100)
    
    soup_top = BeautifulSoup(response_top, 'html.parser')
    soup_bottom = BeautifulSoup(response_bottom, 'html.parser')

    p = Pool(NUMBER_OF_THREADS)

    print('Fetching individual movie data...\nThis might take a while. Go get your coffee!')

    movie_url_list = list(set(
        map(lambda movie: re.sub('\?(.*)', '', movie['href']), soup_top.table.find_all('a'))))

    movie_url_list.extend(list(set(
        map(lambda movie: re.sub('\?(.*)', '', movie['href']), soup_bottom.table.find_all('a')))
    ))
    p.map(retrieve_and_save_movie, movie_url_list[retry_index:])


    # p.close()
    # p.join() # Wait for the workers to die.
    print('Voila!! It is all done now.')


if __name__ == '__main__':
    try:
        repository = Repository()
        repository.create_schema_if_none()
        retry_index = repository.get_num_movies() - 1
        retrieve_movie_list(retry_index=retry_index)
        # retrieve_movie_list()
    except IOError:
        print("Please check your internet connection.")
        # print("Getting retrying step")
        