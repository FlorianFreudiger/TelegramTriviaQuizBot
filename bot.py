import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Poll
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, PicklePersistence
import quiz
import secret

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='log.log')  # Enable logging
logging.debug("Logging enabled")


# InlineKeyboards:

def InlineButtonFromEnum(enum) -> InlineKeyboardButton:
    return InlineKeyboardButton(str(enum), callback_data=enum.__class__.__name__+":"+enum.name)


category_keyboard = [[InlineButtonFromEnum(quiz.QuizCategory.ANY_CATEGORY), InlineButtonFromEnum(quiz.QuizCategory.GENERAL_KNOWLEDGE)],

                     [InlineButtonFromEnum(quiz.QuizCategory.SCIENCE_AND_NATURE), InlineButtonFromEnum(
                         quiz.QuizCategory.ENTERTAINMENT_JAPANESE_ANIME_AND_MANGA)],

                     [InlineButtonFromEnum(quiz.QuizCategory.SCIENCE_COMPUTERS), InlineButtonFromEnum(
                         quiz.QuizCategory.SCIENCE_MATHEMATICS), InlineButtonFromEnum(quiz.QuizCategory.SCIENCE_GADGETS)],

                     [InlineButtonFromEnum(quiz.QuizCategory.ENTERTAINMENT_BOOKS), InlineButtonFromEnum(
                         quiz.QuizCategory.ENTERTAINMENT_FILM), InlineButtonFromEnum(quiz.QuizCategory.ENTERTAINMENT_MUSIC)],

                     [InlineButtonFromEnum(quiz.QuizCategory.ENTERTAINMENT_CARTOON_AND_ANIMATIONS), InlineButtonFromEnum(quiz.QuizCategory.MYTHOLOGY), InlineButtonFromEnum(
                         quiz.QuizCategory.ENTERTAINMENT_MUSICALS_AND_THEATRES)],

                     [InlineButtonFromEnum(quiz.QuizCategory.ENTERTAINMENT_BOARD_GAMES), InlineButtonFromEnum(
                         quiz.QuizCategory.ENTERTAINMENT_VIDEO_GAMES), InlineButtonFromEnum(quiz.QuizCategory.ENTERTAINMENT_TELEVISION)],

                     [InlineButtonFromEnum(quiz.QuizCategory.ENTERTAINMENT_COMICS), InlineButtonFromEnum(
                         quiz.QuizCategory.ART), InlineButtonFromEnum(quiz.QuizCategory.CELEBRITIES)],

                     [InlineButtonFromEnum(quiz.QuizCategory.GEOGRAPHY), InlineButtonFromEnum(
                         quiz.QuizCategory.HISTORY), InlineButtonFromEnum(quiz.QuizCategory.POLITICS)],

                     [InlineButtonFromEnum(quiz.QuizCategory.SPORTS), InlineButtonFromEnum(quiz.QuizCategory.ANIMALS), InlineButtonFromEnum(quiz.QuizCategory.VEHICLES)]]
category_reply_markup = InlineKeyboardMarkup(
    category_keyboard, one_time_keyboard=True)


difficulty_keyboard = [[InlineButtonFromEnum(quiz.QuizDifficulty.ANY)],
                       [InlineButtonFromEnum(quiz.QuizDifficulty.EASY), InlineButtonFromEnum(quiz.QuizDifficulty.MEDIUM), InlineButtonFromEnum(quiz.QuizDifficulty.HARD)]]
difficulty_reply_markup = InlineKeyboardMarkup(
    difficulty_keyboard, one_time_keyboard=True)


# Commands:

def command_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Hello!\nUse /quiz to start generate a new quiz.\nSettings: /category and /difficulty')


def command_category(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Please choose a category:', reply_markup=category_reply_markup, disable_notification=True)


def command_difficulty(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Please choose a difficulty:', reply_markup=difficulty_reply_markup, disable_notification=True)


def command_quiz(update: Update, context: CallbackContext):
    try:
        category = context.chat_data["category"]
    except KeyError:
        category = quiz.QuizCategory.ANY_CATEGORY

    try:
        difficulty = context.chat_data["difficulty"]
    except KeyError:
        difficulty = quiz.QuizDifficulty.ANY

    try:
        newQuiz = quiz.Quiz.fromInternet(category, difficulty)
        question = str(newQuiz.category) + "  - " + str(newQuiz.difficulty) + "\n" + newQuiz.question
        answers, correctIndex = newQuiz.getAnswers()
        # https://python-telegram-bot.readthedocs.io/en/stable/telegram.bot.html#telegram.Bot.send_poll
        pollMessage = context.bot.send_poll(update.effective_chat.id,
                                            question=question,
                                            options=answers,
                                            is_anonymous=False,
                                            type=Poll.QUIZ,
                                            correct_option_id=correctIndex)
    except Exception as exception:
        logging.error(exception)
        update.message.reply_text('💥 Error, could not create poll. 💥')


# Callback queries:

def callbackQueryFunction(update: Update, context: CallbackContext):
    query = update.callback_query

    if query.data.startswith("QuizCategory:"):
        category = quiz.QuizCategory[query.data[13:]]
        context.chat_data["category"] = category
        query.edit_message_text("Quiz category set to " + str(category))

    elif query.data.startswith("QuizDifficulty:"):
        difficulty = quiz.QuizDifficulty[query.data[15:]]
        context.chat_data["difficulty"] = difficulty
        query.edit_message_text("Quiz difficulty set to " + str(difficulty))

    else:
        logging.warning("Unknown callback query: "+query.data)
        query.answer()


# Create Persistence
bot_persistence = PicklePersistence(filename='data.pickle')

logging.info("Starting bot...")
# Create the EventHandler and pass it your bot's token.
updater = Updater(token=secret.api_key(), use_context=True, persistence=bot_persistence)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# command handlers
dispatcher.add_handler(CommandHandler("start", command_start))
dispatcher.add_handler(CommandHandler("quiz", command_quiz))
dispatcher.add_handler(CommandHandler("category", command_category))
dispatcher.add_handler(CommandHandler("difficulty", command_difficulty))
dispatcher.add_handler(CallbackQueryHandler(callbackQueryFunction))

# Start the Bot
updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()
