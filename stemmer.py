import Stemmer as MainStemmer


class Stemmer:
    def __init__(self):
        self.__stemmer = MainStemmer.Stemmer("english")
        self.__cache = {}

    def stem(self, token):
        # Assumes token is lowercase (will just take extra time/space if not)
        if token not in self.__cache:
            self.__cache[token] = self.__stemmer.stemWord(token)

        return self.__cache[token]
