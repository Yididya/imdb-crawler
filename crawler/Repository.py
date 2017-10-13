from sqlalchemy import *
from settings import DATABASE

class Repository:
    def __init__(self, showLog = False):
        """
        Initialize database structure
        """

        self.__showLog = showLog
        self.__engine = create_engine('mysql+pymysql://' + DATABASE['USER'] + ':' + DATABASE['PASSWORD'] + '@localhost:' + DATABASE['PORT'] + '/MovieDB?charset=utf8mb4', echo=self.__showLog)
        self.__metadata = MetaData()

        self.__persons = Table('person', self.__metadata,
            Column('id', Integer, primary_key = True),
            Column('name', String(255), nullable = False, unique = True)
        )

        self.__movies = Table('movie', self.__metadata,
            Column('id', Integer, primary_key = True),
            Column('title', String(255), nullable = False, unique = True),
            Column('imdb_link', String(255), nullable = False, unique = True),
            Column('release_date', Date, nullable = True),
            Column('rating', Float, nullable = True),
            Column('synopsis', Text, nullable = True),
            Column('running_time', String(10), nullable=False, unique=True),
            Column('budget', String(10), nullable=False, unique=True),
            Column('gross_usa', String(20), nullable=False, unique=True),
            Column('gross_worldwide', String(20), nullable=False, unique=True),
            Column('genre', String(50), nullable=False, unique=True)
        )
        self.__actors = Table('Actor', self.__metadata, 
            Column('id', Integer, primary_key = True),
            Column('person_id', Integer, primary_key = True),
            Column('full_name', String(255), nullable=False),
            Column('short_bio', Text, nullable=False),
            Column('birth_date', Date, nullable=True),
            Column('birth_place', String(255), nullable=True),
            Column('known_for', String(300), nullable=True),
            Column('height', Float, nullable=True)
        )
        self.__actor_characters = Table('Actor', self.__metadata,
            Column('id', Integer, primary_key = True),
            Column('person_id', None, ForeignKey('Person.Id')),
            Column('movie_id', None, ForeignKey('Movie.Id')),
            Column('character_name', String(255), nullable = True)
        )

        self.__directors = Table('Director', self.__metadata,
            Column('id', Integer, primary_key = True),
            Column('person_id', None, ForeignKey('Person.Id')),
            Column('movie_id', None, ForeignKey('Movie.Id'))
        )

        self.__reviews = Table('Review', self.__metadata,
            Column('id', Integer, primary_key=True),
            Column('movie_id', None, ForeignKey('Person.Id')),
            Column('review_title', Text, nullable=True),
            Column('review_detail', Text, nullable=True),
        )

    def createSchema(self):
        """
        Create schema in database.
        """
        self.__metadata.drop_all(self.__engine)
        self.__metadata.create_all(self.__engine)

    # Person methods
    def getPersonId(self, name):
        result = self.__engine.connect().execute(
            select([self.__persons.c.Id],
                and_(self.__persons.c.Name == name)
            )
        )

        firstRow = result.fetchone()

        if firstRow == None:
            return None
        else:
            return firstRow[0]

    def savePerson(self, name):
        result = self.__engine.connect().execute(
            self.__persons.insert()
            .values(Name = name)
        )

        return result.inserted_primary_key[0]

#    def updatePerson(self, id, name):
#        conn = self.__engine.connect()
#
#        conn.execute(
#            self.__persons.update().
#            where(self.__persons.c.Id == id).
#            values(Name = name)
#        )

    def savepersonIfDoesntExist(self, name):
        personId = self.getPersonId(name)

        if personId == None:
            return self.savePerson(name)
        else:
            return personId

    # Movie methods
    def getMovieId(self, title):
        result = self.__engine.connect().execute(
            select([self.__movies.c.Id],
                and_(self.__movies.c.Title == title)
            )
        )

        firstRow = result.fetchone()

        if firstRow == None:
            return None
        else:
            return firstRow[0]

    def insertMovie(self, movie):
        result = self.__engine.connect().execute(
            self.__movies.insert()
            .values(Title = movie.Title,
                    ImdbLink = movie.ImdbLink,
                    ReleaseDate = movie.ReleaseDate,
                    Rating = movie.Rating,
                    Synopsis = movie.Synopsis)
        )

        return result.inserted_primary_key[0]

    def saveMovie(self, movie):
        movieId = self.getMovieId(movie.Title)

        if movieId == None:
            movieId = self.insertMovie(movie)

        for directorName in movie.Directors:
            self.saveDirector(movieId, directorName)

        for cast in movie.Actors:
            self.saveActor(movieId, cast['actor'], cast['character'])
        
        for review in movie.Reviews:
            self.saveReview(movieId, review)

    # Director methods
    def saveDirector(self, movieId, directorName):
        personId = self.savepersonIfDoesntExist(directorName)
        result = self.__engine.connect().execute(
            self.__directors.insert()
            .values(Movie_id = movieId, Person_id = personId)
        )

        return result.inserted_primary_key[0]

    # Actor methods
    def saveActor(self, movieId, actorName, characterName):
        personId = self.savepersonIfDoesntExist(actorName)

        result = self.__engine.connect().execute(
            self.__actors.insert()
            .values(Movie_id = movieId, Person_id = personId, CharacterName = characterName)
        )

        return result.inserted_primary_key[0]

    def saveReview(self, movieId, review):
        result = self.__engine.connect().execute(
            self.__reviews.insert()
            .values(movie_id=movieId, review_title=review['title'], review_detail=review['detail'])
        )

        return result.inserted_primary_key[0]

    
