IMDB Crawler
===========

IMDB crawler to get data to create a local movie database.

Retrieves Top 250 and Bottom 100 movie lists and stores data into a MySQL database:
- Movie: title, IMDB link, release date, IMDB rating, synopsis, directors,  actors, characters.

## Requirements
- bs4=4.51
- sqlalchemy=1.1.13
- mysql-connector=2.0.4

## Installation
`pip install -r requirement.txt`

## Setup Database Configuration
Setup your database `USERNAME, PASSWORD and NAME' in `crawler/settings.py`

## Running the crawler
`cd imdb-crawler && python crawler/Crawler.py`
