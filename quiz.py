import logging
import json
import html
import random
import urllib.request
from enum import Enum, unique


@unique
class QuizDifficulty(Enum):
    ANY = -1
    EASY = 0
    MEDIUM = 1
    HARD = 2

    def __str__(self):
        if self == QuizDifficulty.ANY:
            return "🌈 Any Difficulty"
        elif self == QuizDifficulty.EASY:
            return "🥉 Easy"
        elif self == QuizDifficulty.MEDIUM:
            return "🥈 Medium"
        elif self == QuizDifficulty.HARD:
            return "🥇 Hard"
        else:
            logging.error("QuizDifficulty is weird.")
            return "ERROR"

    def toUrlPart(self) -> str:
        if self == QuizDifficulty.ANY:
            return ""
        elif self == QuizDifficulty.EASY:
            return "&difficulty=easy"
        elif self == QuizDifficulty.MEDIUM:
            return "&difficulty=medium"
        elif self == QuizDifficulty.HARD:
            return "&difficulty=hard"
        else:
            logging.error("Unknown QuizDifficulty.")
            return ""


@unique
class QuizCategory(Enum):
    ANY_CATEGORY = 0
    GENERAL_KNOWLEDGE = 9
    ENTERTAINMENT_BOOKS = 10
    ENTERTAINMENT_FILM = 11
    ENTERTAINMENT_MUSIC = 12
    ENTERTAINMENT_MUSICALS_AND_THEATRES = 13
    ENTERTAINMENT_TELEVISION = 14
    ENTERTAINMENT_VIDEO_GAMES = 15
    ENTERTAINMENT_BOARD_GAMES = 16
    SCIENCE_AND_NATURE = 17
    SCIENCE_COMPUTERS = 18
    SCIENCE_MATHEMATICS = 19
    MYTHOLOGY = 20
    SPORTS = 21
    GEOGRAPHY = 22
    HISTORY = 23
    POLITICS = 24
    ART = 25
    CELEBRITIES = 26
    ANIMALS = 27
    VEHICLES = 28
    ENTERTAINMENT_COMICS = 29
    SCIENCE_GADGETS = 30
    ENTERTAINMENT_JAPANESE_ANIME_AND_MANGA = 31
    ENTERTAINMENT_CARTOON_AND_ANIMATIONS = 32

    def __str__(self):
        if self == QuizCategory.ANY_CATEGORY:
            return "🌐 ANYTHING"
        elif self == QuizCategory.GENERAL_KNOWLEDGE:
            return "💡 General knowledge"
        elif self == QuizCategory.ENTERTAINMENT_BOOKS:
            return "📚 Books"
        elif self == QuizCategory.ENTERTAINMENT_FILM:
            return "🎬 Film"
        elif self == QuizCategory.ENTERTAINMENT_MUSIC:
            return "🎶 Music"
        elif self == QuizCategory.ENTERTAINMENT_MUSICALS_AND_THEATRES:
            return "🎭 Theater"
        elif self == QuizCategory.ENTERTAINMENT_TELEVISION:
            return "📺 TV"
        elif self == QuizCategory.ENTERTAINMENT_VIDEO_GAMES:
            return "👾 Games"
        elif self == QuizCategory.ENTERTAINMENT_BOARD_GAMES:
            return "🎲 Games"
        elif self == QuizCategory.SCIENCE_AND_NATURE:
            return "🧬 Science&Nature"
        elif self == QuizCategory.SCIENCE_COMPUTERS:
            return "🖥 Computers"
        elif self == QuizCategory.SCIENCE_MATHEMATICS:
            return "🧮 Math"
        elif self == QuizCategory.MYTHOLOGY:
            return "🌩️ Mythology"
        elif self == QuizCategory.SPORTS:
            return "⚽ Sports"
        elif self == QuizCategory.GEOGRAPHY:
            return "🌍 Geography"
        elif self == QuizCategory.HISTORY:
            return "⌛️ History"
        elif self == QuizCategory.POLITICS:
            return "🗳️ Politics"
        elif self == QuizCategory.ART:
            return "🎨 Art"
        elif self == QuizCategory.CELEBRITIES:
            return "👠 Celebrities"
        elif self == QuizCategory.ANIMALS:
            return "🐢 Animals"
        elif self == QuizCategory.VEHICLES:
            return "🚗 Vehicles"
        elif self == QuizCategory.ENTERTAINMENT_COMICS:
            return "💭 Comics"
        elif self == QuizCategory.SCIENCE_GADGETS:
            return "📱 Gadgets"
        elif self == QuizCategory.ENTERTAINMENT_JAPANESE_ANIME_AND_MANGA:
            return "⛩ Anime&Manga"
        elif self == QuizCategory.ENTERTAINMENT_CARTOON_AND_ANIMATIONS:
            return "📼 Animations"
        else:
            logging.error("Unknown QuizCategory.")
            return ""

    def toUrlPart(self) -> str:
        if self == QuizCategory.ANY_CATEGORY:
            return ""
        else:
            return "&category="+str(self.value)


class Quiz:
    def __init__(self, category: QuizCategory, quizType: int, difficulty: QuizDifficulty, question: str, correctAnswer: str, incorrectAnswers):
        self.category = category
        self.quizType = quizType
        self.difficulty = difficulty
        self.question = question
        self.correctAnswer = correctAnswer
        self.incorrectAnswers = incorrectAnswers

    @staticmethod
    def fromInternet(category=QuizCategory.ANY_CATEGORY, difficulty=QuizDifficulty.ANY):
        url = "https://opentdb.com/api.php?amount=1" + \
            category.toUrlPart() + difficulty.toUrlPart()
        logging.info("Requesting: "+url)

        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read())

        logging.info(data)

        responseCode = data['response_code']
        if responseCode != 0:
            logging.error("Response code: "+str(responseCode))
            return False

        result = data['results'][0]

        # Unescape html characters
        question = html.unescape(result['question'])
        correct_answer = html.unescape(result['correct_answer'])
        incorrect_answers = []
        for incorrect_answer in result['incorrect_answers']:
            incorrect_answers.append(html.unescape(incorrect_answer))

        return True, Quiz(result['category'], result['type'], result['difficulty'], question, correct_answer, incorrect_answers)

    def getAnswers(self):
        if self.quizType == 'multiple':
            answers = self.incorrectAnswers[:]
            random.shuffle(answers)

            correctIndex = random.randint(0, len(answers))
            answers.insert(correctIndex, self.correctAnswer)
            return answers, correctIndex

        elif self.quizType == 'boolean':
            answers = ["True", "False"]
            if self.correctAnswer == 'True':
                return answers, 0
            else:
                return answers, 1

        else:
            logging.error("quizType is neither 'multiple' nor 'boolean'")
