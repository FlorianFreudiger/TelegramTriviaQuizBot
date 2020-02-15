from __future__ import annotations
import logging
import json
import html
import random
import urllib.request
from enum import Enum, unique
from typing import List


@unique
class QuizDifficulty(Enum):
    ANY = -1
    EASY = 0
    MEDIUM = 1
    HARD = 2

    def __str__(self) -> str:
        if self == QuizDifficulty.ANY:
            return "🌈 Any Difficulty"
        elif self == QuizDifficulty.EASY:
            return "🥉 Easy"
        elif self == QuizDifficulty.MEDIUM:
            return "🥈 Medium"
        elif self == QuizDifficulty.HARD:
            return "🥇 Hard"
        else:
            logging.error("Unknown QuizDifficulty.")
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

    def __str__(self) -> str:
        try:
            return QuizCategoryToStr_dict[self]
        except KeyError:
            logging.error("QuizCategoryToStr_dict does not contain " + super().__str__())
            return "Error converting QuizCategory enum to string"

    def toUrlPart(self) -> str:
        if self == QuizCategory.ANY_CATEGORY:
            return ""
        else:
            return "&category="+str(self.value)


QuizCategoryToStr_dict = {QuizCategory.ANY_CATEGORY: "🌐 ANYTHING",
                          QuizCategory.GENERAL_KNOWLEDGE: "💡 General knowledge",
                          QuizCategory.ENTERTAINMENT_BOOKS: "📚 Books",
                          QuizCategory.ENTERTAINMENT_FILM: "🎬 Film",
                          QuizCategory.ENTERTAINMENT_MUSIC: "🎶 Music",
                          QuizCategory.ENTERTAINMENT_MUSICALS_AND_THEATRES: "🎭 Theater",
                          QuizCategory.ENTERTAINMENT_TELEVISION: "📺 TV",
                          QuizCategory.ENTERTAINMENT_VIDEO_GAMES: "👾 Games",
                          QuizCategory.ENTERTAINMENT_BOARD_GAMES: "🎲 Games",
                          QuizCategory.SCIENCE_AND_NATURE: "🧬 Science&Nature",
                          QuizCategory.SCIENCE_COMPUTERS: "🖥 Computers",
                          QuizCategory.SCIENCE_MATHEMATICS: "🧮 Math",
                          QuizCategory.MYTHOLOGY: "🌩️ Mythology",
                          QuizCategory.SPORTS: "⚽ Sports",
                          QuizCategory.GEOGRAPHY: "🌍 Geography",
                          QuizCategory.HISTORY: "⌛️ History",
                          QuizCategory.POLITICS: "🗳️ Politics",
                          QuizCategory.ART: "🎨 Art",
                          QuizCategory.CELEBRITIES: "👠 Celebrities",
                          QuizCategory.ANIMALS: "🐢 Animals",
                          QuizCategory.VEHICLES: "🚗 Vehicles",
                          QuizCategory.ENTERTAINMENT_COMICS: "💭 Comics",
                          QuizCategory.SCIENCE_GADGETS: "📱 Gadgets",
                          QuizCategory.ENTERTAINMENT_JAPANESE_ANIME_AND_MANGA: "⛩ Anime&Manga",
                          QuizCategory.ENTERTAINMENT_CARTOON_AND_ANIMATIONS: "📼 Animations"}


class Quiz:
    def __init__(self, category: QuizCategory, quizType: int, difficulty: QuizDifficulty, question: str, correctAnswer: str, incorrectAnswers: List[str]):
        self.category = category
        self.quizType = quizType
        self.difficulty = difficulty
        self.question = question
        self.correctAnswer = correctAnswer
        self.incorrectAnswers = incorrectAnswers

    @staticmethod
    def fromInternet(category=QuizCategory.ANY_CATEGORY, difficulty=QuizDifficulty.ANY) -> Quiz:
        url = "https://opentdb.com/api.php?amount=1" + \
            category.toUrlPart() + difficulty.toUrlPart()
        logging.info("Requesting: "+url)

        try:
            with urllib.request.urlopen(url) as url:
                data = json.loads(url.read())
        except:
            logging.error("Exception occurred fetching question(s)!")
            return

        logging.info(data)

        responseCode = data['response_code']
        if responseCode != 0:
            logging.warning(
                "Response code: Expected 0 but got "+str(responseCode))

        result = data['results'][0]

        # Unescape html characters
        question = html.unescape(result['question'])
        correct_answer = html.unescape(result['correct_answer'])
        incorrect_answers = []
        for incorrect_answer in result['incorrect_answers']:
            incorrect_answers.append(html.unescape(incorrect_answer))

        return Quiz(result['category'], result['type'], result['difficulty'], question, correct_answer, incorrect_answers)

    def getAnswers(self) -> Tuple[List[str], int]:
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
