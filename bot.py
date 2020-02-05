import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import quiz
import secret

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='log.log')  # Enable logging
logging.debug("Logging enabled")


# InlineKeyboards:

def CatIButton(category) -> InlineKeyboardButton:
    return InlineKeyboardButton(str(category), callback_data="category:"+category.name)


category_keyboard = [[CatIButton(quiz.QuizCategory.ANY_CATEGORY)],
                     [CatIButton(quiz.QuizCategory.GENERAL_KNOWLEDGE), CatIButton(
                         quiz.QuizCategory.SCIENCE_AND_NATURE), CatIButton(quiz.QuizCategory.MYTHOLOGY)],
                     [CatIButton(quiz.QuizCategory.SCIENCE_COMPUTERS), CatIButton(
                         quiz.QuizCategory.SCIENCE_MATHEMATICS), CatIButton(quiz.QuizCategory.SCIENCE_GADGETS)],
                     [CatIButton(quiz.QuizCategory.ENTERTAINMENT_BOOKS), CatIButton(
                         quiz.QuizCategory.ENTERTAINMENT_FILM), CatIButton(quiz.QuizCategory.ENTERTAINMENT_MUSIC)],
                     [CatIButton(quiz.QuizCategory.ENTERTAINMENT_CARTOON_AND_ANIMATIONS), CatIButton(
                         quiz.QuizCategory.ENTERTAINMENT_JAPANESE_ANIME_AND_MANGA), CatIButton(quiz.QuizCategory.ENTERTAINMENT_MUSICALS_AND_THEATRES)],
                     [CatIButton(quiz.QuizCategory.ENTERTAINMENT_BOARD_GAMES), CatIButton(
                         quiz.QuizCategory.ENTERTAINMENT_VIDEO_GAMES), CatIButton(quiz.QuizCategory.ENTERTAINMENT_TELEVISION)],
                     [CatIButton(quiz.QuizCategory.ENTERTAINMENT_COMICS), CatIButton(
                         quiz.QuizCategory.ART), CatIButton(quiz.QuizCategory.CELEBRITIES)],
                     [CatIButton(quiz.QuizCategory.GEOGRAPHY), CatIButton(
                         quiz.QuizCategory.HISTORY), CatIButton(quiz.QuizCategory.POLITICS)],
                     [CatIButton(quiz.QuizCategory.SPORTS), CatIButton(quiz.QuizCategory.ANIMALS), CatIButton(quiz.QuizCategory.VEHICLES)]]
category_reply_markup = InlineKeyboardMarkup(
    category_keyboard, one_time_keyboard=True)


difficulty_keyboard = [[InlineKeyboardButton("Any Difficulty", callback_data="difficulty:-1")],
                       [InlineKeyboardButton("Easy", callback_data="difficulty:0"), InlineKeyboardButton("Medium", callback_data="difficulty:1"), InlineKeyboardButton("Hard", callback_data="difficulty:2")]]
difficulty_reply_markup = InlineKeyboardMarkup(
    difficulty_keyboard, one_time_keyboard=True)


# Commands:

def command_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Hello!\nUse /quiz to start generate a new quiz.\nSettings: /category and /difficulty')


def command_category(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Please choose category:', reply_markup=category_reply_markup, disable_notification=True)


def command_difficulty(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Please choose difficulty:', reply_markup=difficulty_reply_markup, disable_notification=True)


def command_quiz(update: Update, context: CallbackContext):
    if "category" in context.chat_data:
        category = context.chat_data["category"]
    else:
        category = quiz.QuizCategory.ANY_CATEGORY

    if "difficulty" in context.chat_data:
        difficulty = context.chat_data["difficulty"]
    else:
        difficulty = quiz.QuizDifficulty.ANY

    success, newQuiz = quiz.Quiz.fromInternet(
        category=category, difficulty=difficulty)
    if (success):
        answers, correctIndex = newQuiz.getAnswers()
        # https://python-telegram-bot.readthedocs.io/en/stable/telegram.bot.html#telegram.Bot.send_poll
        pollMessage = context.bot.send_poll(
            update.effective_chat.id, newQuiz.question, answers)
        # Quizzes are not yet availibe in the python-telegram-bot api, for now just send the solution after 90 seconds
        context.job_queue.run_once(delayedReplyMessage, 60, context=[
                                   pollMessage, "Correct answer: "+str(correctIndex+1)+". option"])

    else:
        update.message.reply_text('Error, cannot create poll.')


def delayedReplyMessage(context: CallbackContext):
    context.job.context[0].reply_text(context.job.context[1], disable_notification=True)
    context.bot.stop_poll(
        context.job.context[0].chat.id, context.job.context[0].message_id)


# Callback queries:

def callbackQueryFunction(update: Update, context: CallbackContext):
    query = update.callback_query

    if query.data.startswith("category:"):
        category = quiz.QuizCategory[query.data[9:]]
        context.chat_data["category"] = category
        query.edit_message_text("Quiz category set to "+str(category))

    elif query.data.startswith("difficulty:"):
        difficulty = quiz.QuizDifficulty(int(query.data[11:]))
        context.chat_data["difficulty"] = difficulty
        query.edit_message_text("Quiz difficulty set to "+str(difficulty))

    else:
        logging.warning("Unknown callback query: "+query.data)
        query.answer()


logging.info("Starting bot...")
# Create the EventHandler and pass it your bot's token.
updater = Updater(token=secret.api_key(), use_context=True)

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
