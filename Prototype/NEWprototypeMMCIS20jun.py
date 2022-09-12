import logging, csv

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Update, \
    InputMediaPhoto
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

from operator import attrgetter
from difflib import SequenceMatcher
from random import randint

from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


#_______________________RETURN CODES (useful for identifying next function to be called)_________

USERCHOICEMODALITY, PROCESSUSERCONSTRAINTS, FIRSTBRANCH, FIRSTBRANCH2, FUNCTCALLBACK2, SECONDBRANCH, SECONDBRANCH2, SECONDBRANCH3, SECONDBRANCH4, PROCESSING, AFTERRECOMMENDATION, FINALRATINGS, FUNCTCALLBACK = range(13) #removed state: USERCHOICEMACROCATEGORY

#_______________________GLOBAL VARIABLES_________________________________________________________
# further step -> we are moving to multi-user scenario, so we need to better handle global variables:
# we need to use a GLOBAL DICTIONARY which contains for each key (CHATID/USERID) a dictionary of variables (key) and values valid for that user

#GLOBAL DICT FOR EACH USER chatid:dictionaryOfVariables
usersGlobalVariables = {}

menu = [] #list which is filled with all the Piatto objects -> STARTING MENU

#dictionary of macro category names (associate names shown to user with symbolic names in the Piatto object's attribute value)
macroCategNames = {
  "Pasta 🍝": "Pasta",
  "Salad 🥗": "Salad",
  "Dessert 🧁": "Dessert",
  "Snack 🍟": "Snack"
}

#_________GLOBAL VARS: no more used as unique global, but key of global dictionary entry for each user (that is a dict)__________

#User study metrics variables

# counterInteractionTurns ---> useful for user study metrics, it counts the number of turns during the conversation -> important for final step where users are asked to choose and could continue scanning
# startSessionDate ---> useful for user study metrics, it contains conversation start date
# numberSkips ---> useful for user study metrics, number of times user has skipped dishes proposed in preference elicitation step
# numberLikes ---> useful for user study metrics, number of times user liked dishes proposed in preference elicitation step (OPTIMAL VALUE = 5)

#Other variables

# firstUserChoice ---> take into account first user choice (***random for user study***)
# menuAfterConstraintsCheck ---> filtered list generated starting from menu -> constraints and macro categ
# recommendationObjectList ---> final sorted list containing the possible dish to recommend to user
# userChoiceModalityGlobal ---> take into account user choice (send pic, T, MM, MMLAB)
# userChoiceMacroCategoryGlobal ---> None take into account food macro category (e.g. pasta) the user wants to eat
# userRates ---> dictionary containing key:value pairs -> numero of Piatto: rate of user in stars (1,2,3,4 or 5)
# path ---> useful to recall the location where user photos are stored
# flagCheckGotFirstBranch2 ---> flag that tells we got the firstBranch2 function. No skip sending images detected
# flagSkipped ---> flag that tells we skip sending images
# flagSkippedAl ---> flag that tells we skip allergies (user has no constraints on diseases, allergies on specific ingreds)
# flagTextualVisualChoice ---> flag for modality: if False user chooses textual, if True visual
# memoryConstraints ---> store constraints provided by user
# dishToRecommend ---> first element of recommendation list that is shown to user
# nextInd ---> index useful in order to scan the recommendation list
# listConstraintsTap ---> list of constraints the user declares by tsapping on their name (a sort of checkboxes)
# userProfileIngrAndScores ---> list of zip of name ingr and corresp user profile scores
# boolFirstConstr ---> useful in why did you recommend this
# ingrTfIdfOverTresholdWithSpaces ---> useful for recommendation explanation step (contains ingr with score > treshold)
# keyboardIntolerancesDiseases ---> inline keyboard for diseases and intolerances
# dishesToShow ---> length of menuafterconstraints
# counterDishesPrefElic ---> counter dishes shown in preference elicitation step
# flagEmergencyRecommendation ---> tell us the user has not provided 5 rates, but less. (Causes: small menu due to constraints, a lot of skips...)
# listaDishesLiked ---> collect numero of dishes liked by the user


#_______________________CLASS DEFINITION_____________________________________________

class Piatto:
    def __init__(self, numero, nome, ingredienti, immagine, calorie, macroCategoria, servings, totalGramWeight, protein100, carb100, fiber100, sugar100, fat100, satfat100, salt100, kj100, nutri_score, FSAscore, FSAlabel, mediaReviews, numeroReviews, idDishUrl, goodImage, badImage):
        self.numero = numero
        self.nome = nome
        self.ingredienti = ingredienti
        self.immagine = immagine
        self.calorie = calorie
        self.macroCategoria = macroCategoria
        self.servings = servings
        self.totalGramWeight = totalGramWeight
        self.protein100 = protein100
        self.carb100 = carb100
        self.fiber100 = fiber100
        self.sugar100 = sugar100
        self.fat100 = fat100
        self.satfat100 = satfat100
        self.salt100 = salt100
        self.kj100 = kj100
        self.nutriScore = nutri_score
        self.FSAscore = FSAscore
        self.FSAlabel = FSAlabel
        self.mediaReviews = mediaReviews
        self.numeroReviews = numeroReviews
        self.idDishUrl = idDishUrl
        self.goodImage = goodImage
        self.badImage = badImage

#_______________________FUNCTIONS__________________________________________________

#FUNC: fill the list menu with all the available dishes

def creaMenu()-> None:

    datasets = ["pasta_500_rev_7.csv", "salad_500_rev_7.csv", "dessert_500_rev_7.csv", "snack_500_rev_7.csv"]

    #I add Piatto objects into the menu by getting all rows of all menu files (one for category)

    line_count = 1 #index of dishes into the menu
    global menu

    #numero, nome, ingredienti, immagine, calorie, macroCategoria, servings, totalGramWeight, protein100, carb100, fiber100, sugar100, fat100, satfat100, salt100, kj100, nutri_score, FSAscore, FSAlabel, mediaReviews, numReviews, idUrlDish, goodImage, badImage
    for urlDataset in datasets:
        csv_file = open(urlDataset)
        csv_reader = csv.reader(csv_file, delimiter=';')

        for row in csv_reader:
            x = row[5]
            x = x.split(',')
            #IMP: there are some ingredients with upper letters, solve with lower() function
            ingrs = [each_string.lower() for each_string in x]
            calor = row[4]
            macroCateg = row[1]
            # numero, nome, ingredienti, immagine, calorie, macroCategoria, servings, totalGramWeight, protein100, carb100, fiber100, sugar100, fat100, satfat100, salt100, kj100, nutri_score, FSAscore, FSAlabel, mediaReviews, numeroReviews, idUrl, goodim, badIma
            menu.append(Piatto(line_count, row[3], ingrs, row[2], calor, macroCateg, row[6], row[15], row[17], row[18], row[19], row[20], row[21], row[22], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[0], row[32], row[33]))

            line_count += 1


#FUNC: defines the indexes for reading the dishes of each catagory

def returnIndexesByMacroCateg(macroCateg):
    start = 0
    finish = 0

    # userChoiceMacroCategoryGlobal
    if macroCateg == "Pasta 🍝":
        start = 0
        finish = 499#500
    elif macroCateg == "Salad 🥗":
        start = 500
        finish = 999#1000
    elif macroCateg == "Dessert 🧁":
        start = 1000
        finish = 1499#1500
    elif macroCateg == "Snack 🍟":
        start = 1500
        finish = 1999#2000

    return start, finish


#FUNC: print menu list (for each element print some attribute)

def stampaMenu()-> None:
    for obj in menu:
        print( obj.numero, obj.nome, obj.ingredienti, obj.immagine, obj.calorie, obj.macroCategoria )


#FUNC: print generic list passed as parameter (for each element print some attribute)

def stampaLista(lista)-> None:
    for obj in lista:
        print( obj.numero, obj.nome, obj.ingredienti, obj.immagine, obj.calorie, obj.macroCategoria)
def retLista(obj):
    return str(obj.numero) + " " + obj.nome + " " + obj.FSAscore + " "+ obj.nutriScore + " " +obj.macroCategoria


#FUNC: print generic list passed as parameter

def stampaVettore(lista) -> None:
    for obj in lista:
        print(obj)


#FUNC: perform similarity evaluation between two strings

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
    

#FUNC: creates a string of comma separated objects contained in a list

def stampaIngredienti(lista):
    stringa = ''
    for obj in lista:
        stringa = stringa+', '+obj
    return stringa


#FUNC: delete content of the folder passed as parameter

def eraseFolderContent(userImagesFolder):
    import os, shutil
    for filename in os.listdir(userImagesFolder):
        file_path = os.path.join(userImagesFolder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


#*FUNC: first function of the chatbot flow -> first setups and food macro category acquisition

def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user

    userIdentifier = str(user.id) #str(update.message.chat.id)
    print("A new user joins! USER ID: ",userIdentifier, "\n\n")

    #CRETE A NEW ENTRY FOR USER and assign an empty dictionary that will be filled during chatbot flow
    global usersGlobalVariables
    usersGlobalVariables[userIdentifier] = {}

    usersGlobalVariables[str(update.message.from_user.id)]["counterInteractionTurns"] = 0
    usersGlobalVariables[str(update.message.from_user.id)]["startSessionDate"] = update.message.date

    reply_keyboard = [['Pasta 🍝'], ['Salad 🥗'], ['Dessert 🧁'], ['Snack 🍟']]
    welcomeString = 'Hi!\n' + 'I will hold a conversation with you to identify the best dish ' \
                                                      'for you. \n\nNote: send /cancel to stop talking to me \n\n' + \
                    'Select a category of food you would like to eat'

    
    update.message.reply_text(welcomeString, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=False))

    return USERCHOICEMODALITY


#*FUNC: function of the chatbot flow -> modality setup and first user constraints acquisition

def userChoiceModality(update: Update, context: CallbackContext) -> int:
    global usersGlobalVariables

    usersGlobalVariables[str(update.message.from_user.id)]["counterInteractionTurns"] = usersGlobalVariables[str(update.message.from_user.id)]["counterInteractionTurns"] + 1
    usersGlobalVariables[str(update.message.from_user.id)]["userChoiceMacroCategoryGlobal"] = update.message.text

    #User study -> Choose index
    # 1 for T,
    # 2 for MM,
    # 3 for MMLAB


    listOfModalities = ["Send your pictures 📸", "Rate dish proposals (textual) ⭐️📝", "Rate dish proposals (visual) ⭐️🍝", "Rate dish proposal (visual+label explan) ✅"]
    usersGlobalVariables[str(update.message.from_user.id)]["userChoiceModalityGlobal"] = listOfModalities[2]
    #RANDOM import random random.choice(listOfModalities)
    #NOT RANDOM AND NOT FIXED update.message.text

    print("User ", str(update.message.from_user.id), " chose ", usersGlobalVariables[str(update.message.from_user.id)]["userChoiceMacroCategoryGlobal"], " category\n")
    print("User ", str(update.message.from_user.id), "is working with modality ", usersGlobalVariables[str(update.message.from_user.id)]["userChoiceModalityGlobal"],"\n")

    usersGlobalVariables[str(update.message.from_user.id)]["keyboardIntolerancesDiseases"] = [
        [InlineKeyboardButton('Lactose', callback_data='0'), InlineKeyboardButton('Meat', callback_data='1'),
         InlineKeyboardButton('Alcohol', callback_data='2')],
        [InlineKeyboardButton('Seafood', callback_data='3'), InlineKeyboardButton('Reflux', callback_data='4'),
         InlineKeyboardButton('Cholest.', callback_data='5')],
        [InlineKeyboardButton('Diabetes', callback_data='6')],
        [InlineKeyboardButton('(Done)', callback_data='7')]]

    usersGlobalVariables[str(update.message.from_user.id)]["listConstraintsTap"] = []
    usersGlobalVariables[str(update.message.from_user.id)]["flagSkipped"] = False
    usersGlobalVariables[str(update.message.from_user.id)]["flagCheckGotFirstBranch2"] = False
    usersGlobalVariables[str(update.message.from_user.id)]["nextInd"] = 0


    reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.message.from_user.id)]["keyboardIntolerancesDiseases"])
    update.message.reply_text(
        'Are you intolerant to something or you have any diseases? Please tap on them if you have any. \nClick on (Done) button to continue\n',
        reply_markup=reply_markup
    )

    return FUNCTCALLBACK


#* functions set of the chatbot flow
#*FUNC: callback query function called when user decides to end first constraint acquisition step -> ask for other specific constraints on ingredients

def goToOtherConstraints(update, context):
    global usersGlobalVariables
    #listConstraintsTap check dim and print values

    usersGlobalVariables[str(update.callback_query.from_user.id)]["counterInteractionTurns"] = usersGlobalVariables[str(update.callback_query.from_user.id)]["counterInteractionTurns"] + 1

    if len(usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"]) > 0:
        stringIntol = "Constraints: "
        i = 0
        for elem in usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"]:
            if i != 0:
                stringIntol += ", "+elem
            else:
                stringIntol += elem
            i += 1
        update.callback_query.message.edit_text(stringIntol)
        print("User ",str(update.callback_query.from_user.id)," has these contraints -> ", usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"],"\n")

        #bool useful later in why didi you recommend this
        usersGlobalVariables[str(update.callback_query.from_user.id)]["boolFirstConstr"] = True
    else:
        print("User ", str(update.callback_query.from_user.id), " has no constraints \n")
        usersGlobalVariables[str(update.callback_query.from_user.id)]["boolFirstConstr"] = False
    update.effective_message.reply_text('Please let me know if you would avoid some ingredients. Write a list of ingredients separated by comma. \nClick on '
                             '/noconstraints if you don\'t have any diet constraint')

    return PROCESSUSERCONSTRAINTS

#*FUNCS: callback query functions called when user clicks on a constraint during first constraint acquisition step

def zero(update, context):
    query = update.callback_query
    reply_markup = ""
    global usersGlobalVariables

    current = usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][0][0].text

    if current == "Lactose":
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][0][0] = InlineKeyboardButton('Lactose ✅', callback_data='0')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].append("Lactose")
    else:
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][0][0] = InlineKeyboardButton('Lactose', callback_data='0')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].remove("Lactose")


    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Are you intolerant to something or you have any diseases? Please tap on them if you have any. \nClick on (Done) button to continue\n",
        reply_markup=reply_markup
    )

    return FUNCTCALLBACK
def one(update, context):
    query = update.callback_query
    reply_markup = ""
    global usersGlobalVariables

    current = usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][0][1].text

    if current == "Meat":
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][0][1] = InlineKeyboardButton('Meat ✅', callback_data='1')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].append("Meat")
    else:
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][0][1] = InlineKeyboardButton('Meat', callback_data='1')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].remove("Meat")


    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Are you intolerant to something or you have any diseases? Please tap on them if you have any. \nClick on (Done) button to continue\n",
        reply_markup=reply_markup
    )

    return FUNCTCALLBACK
def two(update, context):
    query = update.callback_query
    reply_markup = ""
    global usersGlobalVariables

    current = usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][0][2].text

    if current == "Alcohol":
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][0][2] = InlineKeyboardButton('Alcohol ✅', callback_data='2')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].append("Alcohol")
    else:
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][0][2] = InlineKeyboardButton('Alcohol', callback_data='2')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].remove("Alcohol")

    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Are you intolerant to something or you have any diseases? Please tap on them if you have any. \nClick on (Done) button to continue\n",
        reply_markup=reply_markup
    )

    return FUNCTCALLBACK
def three(update, context):
    query = update.callback_query
    reply_markup = ""
    global usersGlobalVariables

    current = usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][1][0].text

    if current == "Seafood":
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][1][0] = InlineKeyboardButton('Seafood ✅', callback_data='3')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].append("Seafood")
    else:
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][1][0] = InlineKeyboardButton('Seafood', callback_data='3')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].remove("Seafood")

    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Are you intolerant to something or you have any diseases? Please tap on them if you have any. \nClick on (Done) button to continue\n",
        reply_markup=reply_markup
    )

    return FUNCTCALLBACK
def four(update, context):
    query = update.callback_query
    reply_markup = ""
    global usersGlobalVariables

    current = usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][1][1].text

    if current == "Reflux":
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][1][1] = InlineKeyboardButton('Reflux ✅', callback_data='4')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].append("Reflux")
    else:
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][1][1] = InlineKeyboardButton('Reflux', callback_data='4')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].remove("Reflux")

    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Are you intolerant to something or you have any diseases? Please tap on them if you have any. \nClick on (Done) button to continue\n",
        reply_markup=reply_markup
    )

    return FUNCTCALLBACK
def five(update, context):
    query = update.callback_query
    reply_markup = ""
    global usersGlobalVariables

    current = usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][1][2].text

    if current == "Cholest.":
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][1][2] = InlineKeyboardButton('Cholest. ✅', callback_data='5')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].append("Cholesterolemia")
    else:
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][1][2] = InlineKeyboardButton('Cholest.', callback_data='5')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].remove("Cholesterolemia")

    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Are you intolerant to something or you have any diseases? Please tap on them if you have any. \nClick on (Done) button to continue\n",
        reply_markup=reply_markup
    )

    return FUNCTCALLBACK
def six(update, context):
    query = update.callback_query
    reply_markup = ""
    global usersGlobalVariables

    current = usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][2][0].text

    if current == "Diabetes":
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][2][0] = InlineKeyboardButton('Diabetes ✅', callback_data='6')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].append("Diabetes")
    else:
        usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"][2][0] = InlineKeyboardButton('Diabetes', callback_data='6')
        reply_markup = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)]["keyboardIntolerancesDiseases"])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listConstraintsTap"].remove("Diabetes")

    bot = context.bot
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Are you intolerant to something or you have any diseases? Please tap on them if you have any. \nClick on (Done) button to continue\n",
        reply_markup=reply_markup
    )

    return FUNCTCALLBACK


#*FUNC: function of the chatbot flow -> process user constraints and filter the menu

def processUserConstraints(update: Update, context: CallbackContext) -> int:

    global usersGlobalVariables
    usersGlobalVariables[str(update.message.from_user.id)]["flagSkippedAl"] = False

    usersGlobalVariables[str(update.message.from_user.id)]["counterInteractionTurns"] = usersGlobalVariables[str(update.message.from_user.id)]["counterInteractionTurns"] + 1

    if update.message.text=="/noconstraints":
        usersGlobalVariables[str(update.message.from_user.id)]["flagSkippedAl"] = True

    if usersGlobalVariables[str(update.message.from_user.id)]["flagSkippedAl"] == False:

        update.message.reply_text('Taking care of your constraints...')

        # user has constraints on diet. Analyze them
        userText = update.message.text
        # imagine diseases separated by comma
        userConstraints = userText.split(',')
        userConstraints = [each_string.lower() for each_string in userConstraints]  # lower case
        userConstraints = [each_string.strip() for each_string in userConstraints]  # remove spaces before and after strings


        userConstraints.extend(usersGlobalVariables[str(update.message.from_user.id)]["listConstraintsTap"]) #add tap of user (consraints disease/intol) to ingr to avoid

        usersGlobalVariables[str(update.message.from_user.id)]["memoryConstraints"] = userConstraints

        #HERE: MENUAFTERCONSTRAINTS FIRST INITIALIZATION
        usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"] = menu.copy()  # start from the entire menu
        
        csv_reader = None
        with open('DiseasesIntolerances.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader, None)  # skip the headers
            csv_reader = list(csv_reader)
        for elem in userConstraints:
            # 1 / REMOVE ALL DISHES WITH INGREDIENTS SPECIFIED BY USER -> es zucchini
            for obj in reversed(usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"]):
                cond = True in (similar(elem, el) >= 0.8 for el in obj.ingredienti) # true se any of them respect condition
                if cond == True:
                    # remove the dish
                    usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"].remove(obj)

            # 2 / REMOVE ALL DISHES CONTAINING SPECIFIED INGREDIENTS OF DISEASES IN THE DISEASE DATASET
    		# scan file of intolerances to check if present a disease/intol like what user has written

            for row in csv_reader:

                nomeDisIntol = row[0]
                if similar(nomeDisIntol, elem) >= 0.7:
                    # if found reflux
                    ingredientsToAvoid = row[2]

                    if ingredientsToAvoid != '':

                        listaIngrAvoid = ingredientsToAvoid.split(',')
                        lungh = len(listaIngrAvoid)

                        # for all not recommended ingredients due to disease/allergy
                        for i in range(0, lungh):

                            ingredToBeRomoved = listaIngrAvoid[i]
                            # reversed to avoid problem with indexes (when removing elements)

                            for obj in reversed(usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"]):

                                # if ingredToBeRomoved in obj.ingredienti:
                                cond = True in (similar(ingredToBeRomoved, el) >= 0.8 for el in
                                                obj.ingredienti)  # true if any of them respect condition
                                if cond == True:
                                    # at least one respects the condition
                                    usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"].remove(obj)  # removed dish with ingredient not avoided

                    break  #quit if found similar to that user constraint

    else:
        update.message.reply_text('Taking care of your constraints...')
        userConstraints =  usersGlobalVariables[str(update.message.from_user.id)]["listConstraintsTap"]

        usersGlobalVariables[str(update.message.from_user.id)]["memoryConstraints"] = userConstraints
        usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"] = menu.copy()

        csv_reader = None
        with open('DiseasesIntolerances.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader, None)  # skip the headers
            csv_reader = list(csv_reader)
        for elem in userConstraints:

            # 1 / REMOVE ALL DISHES WITH INGREDIENTS SPECIFIED BY USER (es. "I am allergic to zucchini") -> OUT: zucchini

            for obj in reversed(usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"]):
                cond = True in (similar(elem, el) >= 0.8 for el in
                                obj.ingredienti)  # true se any of them respect condition
                if cond == True:
                    # remove the dish
                    usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"].remove(obj)

            # 2 / REMOVE ALL DISHES CONTAINING SPECIFIED INGREDIENTS OF DISEASES IN THE DISEASE DATASET
            # scan file of intolerances to check if present a disease/intol like what user has written

            for row in csv_reader:

                nomeDisIntol = row[0]
                if similar(nomeDisIntol, elem) >= 0.7:
                    # if found reflux
                    ingredientsToAvoid = row[2]

                    if ingredientsToAvoid != '':

                        listaIngrAvoid = ingredientsToAvoid.split(',')
                        lungh = len(listaIngrAvoid)

                        # for all not recommended ingredients due to disease/allergy
                        for i in range(0, lungh):

                            ingredToBeRomoved = listaIngrAvoid[i]
                            # reversed to avoid problem with indexes (when removing elements)

                            for obj in reversed(usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"]):

                                # if ingredToBeRomoved in obj.ingredienti:
                                cond = True in (similar(ingredToBeRomoved, el) >= 0.8 for el in
                                                obj.ingredienti)  # true se any of them respect condition
                                if cond == True:
                                    # at least one respects the condition
                                    usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"].remove(obj)  # removed dish with ingredient not avoided

                    break  # quit if found similar to that user constraint


    # remove all dishes not belonging to the macro-category chosen by the user

    usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"] = [p for p in usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"] if
                                 p.macroCategoria == macroCategNames[usersGlobalVariables[str(update.message.from_user.id)]["userChoiceMacroCategoryGlobal"]]]

    print("User ", str(update.message.from_user.id), " has a new menu of lenght ",len(usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"]), "\n")
    #check if empty menu
    if not usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"]:
        print("(ERROR 1) END OF MENU for user ", str(update.message.from_user.id))
        update.message.reply_text('Sorry...I do not have any food recommendation for you')

        #update.message.reply_text('Please send us an email. We will help you completing the task in the available time. \nFollow the link in the Amazon MTurk HIT instructions:')
        #context.bot.send_video(chat_id=update.message.chat_id, video=open('images/support_video.mov','rb'), height = 1288, width=2346, supports_streaming=True, timeout=20, caption="Support instructions")

        del usersGlobalVariables[str(update.message.from_user.id)]
        return ConversationHandler.END

    # NOW MANAGE NEXT STEPS!

    usersGlobalVariables[str(update.message.from_user.id)]["firstUserChoice"] = usersGlobalVariables[str(update.message.from_user.id)]["userChoiceModalityGlobal"]
    user = update.message.from_user

    if usersGlobalVariables[str(update.message.from_user.id)]["firstUserChoice"] == 'Send your pictures 📸':
        update.message.reply_text('Please send me a pic of your favourite food...')
        return FIRSTBRANCH
    else:
        usersGlobalVariables[str(update.message.from_user.id)]["counterDishesPrefElic"] = 1
        usersGlobalVariables[str(update.message.from_user.id)]["numberSkips"] = 0
        usersGlobalVariables[str(update.message.from_user.id)]["numberLikes"] = 0 #IMP DOBBIAMO ARRIVARE A 5 ***
        usersGlobalVariables[str(update.message.from_user.id)]["userRates"] = {}

        idKeyb = "keyboardLikeRandDish"+str(usersGlobalVariables[str(update.message.from_user.id)]["counterDishesPrefElic"])

        usersGlobalVariables[str(update.message.from_user.id)][idKeyb] = [[InlineKeyboardButton('Like', callback_data='Like'),InlineKeyboardButton('Skip', callback_data='Skip')]]

        reply_markupN = InlineKeyboardMarkup(usersGlobalVariables[str(update.message.from_user.id)][idKeyb])


        #**********
        usersGlobalVariables[str(update.message.from_user.id)]["dishesToShow"] = len(usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"])

        if usersGlobalVariables[str(update.message.from_user.id)]["dishesToShow"] > 5:
            update.message.reply_text('From now I will show to you some dishes. Tap on like if you like a dish! Tap on skip otherwise. \n\nI need 5 preferences...', reply_markup=ReplyKeyboardRemove())
            usersGlobalVariables[str(update.message.from_user.id)]["startPreferenceElicitationDate"] = update.message.date
            import random
            random.shuffle(usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"])

            nameDish = usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"][usersGlobalVariables[str(update.message.from_user.id)]["counterDishesPrefElic"]-1].nome
            imgDish = usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"][usersGlobalVariables[str(update.message.from_user.id)]["counterDishesPrefElic"]-1].immagine

            usersGlobalVariables[str(update.message.from_user.id)]["listaDishesLiked"] = []
            usersGlobalVariables[str(update.message.from_user.id)]["listaDishesShown"] = []
            usersGlobalVariables[str(update.message.from_user.id)]["flagEmergencyRecommendation"] = False

            usersGlobalVariables[str(update.message.from_user.id)]["listaDishesShown"].append(usersGlobalVariables[str(update.message.from_user.id)]["menuAfterConstraintsCheck"][usersGlobalVariables[str(update.message.from_user.id)]["counterDishesPrefElic"]-1].idDishUrl)

            if usersGlobalVariables[str(update.message.from_user.id)]["firstUserChoice"] == 'Rate dish proposals (textual) ⭐️📝':
                usersGlobalVariables[str(update.message.from_user.id)]["flagTextualVisualChoice"] = False #utile dopo, non usato qui
                update.message.reply_text(nameDish,reply_markup=reply_markupN)
            elif usersGlobalVariables[str(update.message.from_user.id)]["firstUserChoice"] == 'Rate dish proposals (visual) ⭐️🍝' or usersGlobalVariables[str(update.message.from_user.id)]["firstUserChoice"] == 'Rate dish proposal (visual+label explan) ✅':
                usersGlobalVariables[str(update.message.from_user.id)]["flagTextualVisualChoice"] = True
                update.message.reply_photo(imgDish,reply_markup=reply_markupN, caption=nameDish)


            return FUNCTCALLBACK2
        else:
            print("(ERROR 2) END OF MENU for user ", str(update.message.from_user.id))
            update.message.reply_text('Sorry...I do not have any food recommendation for you')

            #update.message.reply_text('Please send us an email. We will help you completing the task in the available time. \nFollow the link in the Amazon MTurk HIT instructions:')
            #context.bot.send_video(chat_id=update.message.chat_id, video=open('images/support_video.mov', 'rb'), height=1288, width=2346, supports_streaming=True, timeout=20, caption="Support instructions")

            del usersGlobalVariables[str(update.message.from_user.id)]
            return ConversationHandler.END


#*FUNCS: callback query functions called when user clicks on LIke or SKip during preference elicitation step

def likeDishN(update, context):
    query = update.callback_query
    reply_markup = ""
    global usersGlobalVariables

    idKeyb = "keyboardLikeRandDish" + str(usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"])

    current = usersGlobalVariables[str(update.callback_query.from_user.id)][idKeyb][0][0].text

    if current == "Like":
        usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] = usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"]+1
        stringaLiked = 'Liked 👍 ('+str(usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"])+"/5)"
        usersGlobalVariables[str(update.callback_query.from_user.id)][idKeyb][0][0] = InlineKeyboardButton(stringaLiked, callback_data='Like')
        reply_markup = InlineKeyboardMarkup([[usersGlobalVariables[str(update.callback_query.from_user.id)][idKeyb][0][0]]]) #InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)][idKeyb])

        usersGlobalVariables[str(update.callback_query.from_user.id)]["listaDishesLiked"].append(usersGlobalVariables[str(update.callback_query.from_user.id)]["menuAfterConstraintsCheck"][usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"]-1].numero)
        usersGlobalVariables[str(update.callback_query.from_user.id)]["userRates"][usersGlobalVariables[str(update.callback_query.from_user.id)]["menuAfterConstraintsCheck"][usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"]-1].numero-1] = 5


    bot = context.bot

    bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )

    usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"] = usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"] + 1

    if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 5:
        update.effective_message.reply_text("Thank you for providing 5 preferences! Processing recommendations for you...")
        usersGlobalVariables[str(update.callback_query.from_user.id)]["finishPreferenceElicitationDate"] = update.effective_message.date
        usersGlobalVariables[str(update.callback_query.from_user.id)]["counterInteractionTurns"] = usersGlobalVariables[str(update.callback_query.from_user.id)]["counterInteractionTurns"] + 1

        processing(update,context)
        return AFTERRECOMMENDATION
    else:
        # CONDIZIONE PER CONTROLLARE CHE INDICE NON SIA OLTRE DISPOBILITA DI MENUAFTER CONSTRAINT
        if (usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] + usersGlobalVariables[str(update.callback_query.from_user.id)]["numberSkips"]) >= usersGlobalVariables[str(update.callback_query.from_user.id)]["dishesToShow"]:
            if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] > 0:
                #GESTIONE USER PROFILE E MESSAGGIO SIMBOLICO E SOPRATTUTTO FLAGS
                stringa="likes"
                if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 1:
                    stringa = "like"
                update.effective_message.reply_text("Ok, you have provided only ", usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"], stringa,", that is good but not so many. However, I will try to recommend you something...")
                usersGlobalVariables[str(update.callback_query.from_user.id)]["finishPreferenceElicitationDate"] = update.effective_message.date
                usersGlobalVariables[str(update.callback_query.from_user.id)]["flagEmergencyRecommendation"] = True

                processing(update, context)
                return AFTERRECOMMENDATION
            else:
                print("(ERROR 3) END OF MENU for user ", str(update.callback_query.from_user.id))
                update.effective_message.reply_text('Sorry...I do not have any food recommendation for you')

                #update.message.reply_text('Please send us an email. We will help you completing the task in the available time. \nFollow the link in the Amazon MTurk HIT instructions:')
                #context.bot.send_video(chat_id=update.message.chat_id, video=open('images/support_video.mov', 'rb'),height=1288, width=2346, supports_streaming=True, timeout=20,caption="Support instructions")

                del usersGlobalVariables[str(update.callback_query.from_user.id)]
                return ConversationHandler.END
        else:
            idKeyb = "keyboardLikeRandDish" + str(usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"])
            usersGlobalVariables[str(update.callback_query.from_user.id)][idKeyb] = [[InlineKeyboardButton('Like', callback_data='Like'),InlineKeyboardButton('Skip', callback_data='Skip')]]
            reply_markupN = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)][idKeyb])

            nameDish = usersGlobalVariables[str(update.callback_query.from_user.id)]["menuAfterConstraintsCheck"][usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"] - 1].nome
            imgDish = usersGlobalVariables[str(update.callback_query.from_user.id)]["menuAfterConstraintsCheck"][usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"] - 1].immagine

            usersGlobalVariables[str(update.callback_query.from_user.id)]["listaDishesShown"].append(usersGlobalVariables[str(update.callback_query.from_user.id)]["menuAfterConstraintsCheck"][usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"] - 1].idDishUrl)

            if usersGlobalVariables[str(update.callback_query.from_user.id)]["firstUserChoice"] == 'Rate dish proposals (textual) ⭐️📝':
                update.effective_message.reply_text(nameDish, reply_markup=reply_markupN)
            elif usersGlobalVariables[str(update.callback_query.from_user.id)]["firstUserChoice"] == 'Rate dish proposals (visual) ⭐️🍝' or usersGlobalVariables[str(update.callback_query.from_user.id)]["firstUserChoice"] == 'Rate dish proposal (visual+label explan) ✅':
                update.effective_message.reply_photo(imgDish, reply_markup=reply_markupN, caption=nameDish)

            return FUNCTCALLBACK2
def skipDishN(update, context):
    usersGlobalVariables[str(update.callback_query.from_user.id)]["numberSkips"] = usersGlobalVariables[str(update.callback_query.from_user.id)]["numberSkips"]+1

    usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"] =  usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"] + 1

    bot = context.bot
    query = update.callback_query
    reply_markup = InlineKeyboardMarkup([])

    bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )

    if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] <5:

        if (usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] + usersGlobalVariables[str(update.callback_query.from_user.id)]["numberSkips"]) >= usersGlobalVariables[str(update.callback_query.from_user.id)]["dishesToShow"]:

            if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] > 0:
                #GESTIONE USER PROFILE E MESSAGGIO SIMBOLICO E SOPRATTUTTO FLAGS
                stringa=" likes"
                if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 1:
                    stringa = " like"
                risposta = "Ok, you have provided only " + str(usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"]) + stringa+", that is good but not so much. However, I will try to recommend you something..."
                update.effective_message.reply_text(risposta)
                usersGlobalVariables[str(update.callback_query.from_user.id)]["flagEmergencyRecommendation"] = True
                usersGlobalVariables[str(update.callback_query.from_user.id)]["finishPreferenceElicitationDate"] = update.effective_message.date

                processing(update, context)
                return AFTERRECOMMENDATION
            else:
                print("(ERROR 4) END OF MENU for user ", str(update.callback_query.from_user.id))
                update.effective_message.reply_text('Sorry...I do not have any food recommendation for you')

                #update.message.reply_text('Please send us an email. We will help you completing the task in the available time. \nFollow the link in the Amazon MTurk HIT instructions:')
                #context.bot.send_video(chat_id=update.message.chat_id, video=open('images/support_video.mov', 'rb'),height=1288, width=2346, supports_streaming=True, timeout=20,caption="Support instructions")

                del usersGlobalVariables[str(update.callback_query.from_user.id)]
                return ConversationHandler.END
        else:
            idKeyb = "keyboardLikeRandDish" + str(usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"])
            usersGlobalVariables[str(update.callback_query.from_user.id)][idKeyb] = [[InlineKeyboardButton('Like', callback_data='Like'),InlineKeyboardButton('Skip', callback_data='Skip')]]
            reply_markupN = InlineKeyboardMarkup(usersGlobalVariables[str(update.callback_query.from_user.id)][idKeyb])

            nameDish = usersGlobalVariables[str(update.callback_query.from_user.id)]["menuAfterConstraintsCheck"][usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"] - 1].nome
            imgDish = usersGlobalVariables[str(update.callback_query.from_user.id)]["menuAfterConstraintsCheck"][usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"] - 1].immagine

            usersGlobalVariables[str(update.callback_query.from_user.id)]["listaDishesShown"].append(usersGlobalVariables[str(update.callback_query.from_user.id)]["menuAfterConstraintsCheck"][usersGlobalVariables[str(update.callback_query.from_user.id)]["counterDishesPrefElic"] - 1].idDishUrl)


            if usersGlobalVariables[str(update.callback_query.from_user.id)]["firstUserChoice"] == 'Rate dish proposals (textual) ⭐️📝':
                update.effective_message.reply_text(nameDish, reply_markup=reply_markupN)
            elif usersGlobalVariables[str(update.callback_query.from_user.id)]["firstUserChoice"] == 'Rate dish proposals (visual) ⭐️🍝' or usersGlobalVariables[str(update.callback_query.from_user.id)]["firstUserChoice"] == 'Rate dish proposal (visual+label explan) ✅':
                update.effective_message.reply_photo(imgDish, reply_markup=reply_markupN, caption=nameDish)


            return FUNCTCALLBACK2


#*FUNC: function of the chatbot flow -> support for user photo sending (NOT USED)

def firstBranch(update: Update, context: CallbackContext) -> int:
    # save and elaborate user's photos

    file = context.bot.getFile(update.message.photo[-1].file_id)  # get biggest dimension image (there are more than one per each  photo sent by user)
    print("file_id: " + str(update.message.photo[-1].file_id))

    user = update.message.from_user

    import os
    from os import path as pt
    # define the name of the directory to be created
    # global path
    global usersGlobalVariables
    usersGlobalVariables[str(update.message.from_user.id)]["path"] = 'users_photos/' + user.username

    if pt.isdir(usersGlobalVariables[str(update.message.from_user.id)]["path"]) == True:
        eraseFolderContent(usersGlobalVariables[str(update.message.from_user.id)]["path"])

    try:
        os.mkdir(usersGlobalVariables[str(update.message.from_user.id)]["path"])

    except OSError:
        print("Creation of the directory %s failed" % usersGlobalVariables[str(update.message.from_user.id)]["path"])

    else:
        print("Successfully created the directory %s " % usersGlobalVariables[str(update.message.from_user.id)]["path"])

    pathDir = usersGlobalVariables[str(update.message.from_user.id)]["path"] + '/image1.jpg'
    file.download(
        custom_path=pathDir)  # check if file called image1.jpg is still present (or maybe erase content of the folder of user before start)

    update.message.reply_text(
        'Please send me another one...\n Type /skip if you don\'t have more photos or you want to go ahead.')

    return FIRSTBRANCH2


#*FUNC: function of the chatbot flow -> support for user photo sending (NOT USED)

def firstBranch2(update: Update, context: CallbackContext) -> int:
    global usersGlobalVariables
    file = context.bot.getFile(
        update.message.photo[-1].file_id)  # get biggest dimension image (there are more than one)
    print("file_id: " + str(update.message.photo[-1].file_id))

    pathDir = usersGlobalVariables[str(update.message.from_user.id)]["path"] + '/image2.jpg'
    file.download(custom_path=pathDir)

    #global flagCheckGotFirstBranch2

    usersGlobalVariables[str(update.message.from_user.id)]["flagCheckGotFirstBranch2"] = True

    update.message.reply_text(
        'Please send me a last pic...\n Type /skip if you don\'t have more photos or you want to go ahead.')

    return PROCESSING


#FUNC: return useful file names given the macrocategory chosen by user

def returnFilesNamesByMacroCateg(macroCateg):
    ingrNames = None
    dishNames = None
    tfIdfMenu = None

    if macroCateg == "Pasta 🍝":
        ingrNames = "tfIdfIngredientsNamesPasta500.txt"
        dishNames = "tfIdfDishesNamesPasta500.txt"
        tfIdfMenu = "tfIdfMenuPasta500.csv"
    elif macroCateg == "Salad 🥗":
        ingrNames = "tfIdfIngredientsNamesSalad500.txt"
        dishNames = "tfIdfDishesNamesSalad500.txt"
        tfIdfMenu = "tfIdfMenuSalad500.csv"
    elif macroCateg == "Dessert 🧁":
        ingrNames = "tfIdfIngredientsNamesDessert500.txt"
        dishNames = "tfIdfDishesNamesDessert500.txt"
        tfIdfMenu = "tfIdfMenuDessert500.csv"
    elif macroCateg == "Snack 🍟":
        ingrNames = "tfIdfIngredientsNamesSnack500.txt"
        dishNames = "tfIdfDishesNamesSnack500.txt"
        tfIdfMenu = "tfIdfMenuSnack500.csv"

    return ingrNames, dishNames, tfIdfMenu


#*FUNC: function of the chatbot flow -> utilizes all the information provided by user for building a user profile and generating a recommendation list sorted wrt cosine similarity with the user profile

def processing(update: Update, context: CallbackContext) -> int:
    global usersGlobalVariables
    if usersGlobalVariables[str(update.callback_query.from_user.id)]["flagSkipped"] == False:
        if usersGlobalVariables[str(update.callback_query.from_user.id)]["flagCheckGotFirstBranch2"] == True:
            # try catch riparatore :(

            try:
                file = context.bot.getFile(update.message.photo[-1].file_id)  # get biggest dimension image (there are more than one)
                print("file_id: " + str(update.message.photo[-1].file_id))

                pathDir = usersGlobalVariables[str(update.callback_query.from_user.id)]["path"] + '/image3.jpg'
                file.download(custom_path=pathDir)

                # here I can manage images and with a similarity algorithm identify what food it is about (COSINE)
                # however at this stage I already have images, so processing can already take place (IDENTIFY WHAT DISH USER SENT)
            except:
                print('error on missing get of command handler skip')

    # GO TO RECOMMENDATION!!!!

    listOfTuples = list(usersGlobalVariables[str(update.callback_query.from_user.id)]["userRates"].items())

    if usersGlobalVariables[str(update.callback_query.from_user.id)]["flagEmergencyRecommendation"] is True:
        if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 4:
            rate1 = listOfTuples[0][1]  # 5 stars
            rate2 = listOfTuples[1][1]
            rate3 = listOfTuples[2][1]
            rate4 = listOfTuples[3][1]
        elif usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 3:
            rate1 = listOfTuples[0][1]  # 5 stars
            rate2 = listOfTuples[1][1]
            rate3 = listOfTuples[2][1]
        elif usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 2:
            rate1 = listOfTuples[0][1]  # 5 stars
            rate2 = listOfTuples[1][1]
        elif usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 1:
            rate1 = listOfTuples[0][1]  # 5 stars
    else:
        rate1 = listOfTuples[0][1] #Like = 5 stars
        rate2 = listOfTuples[1][1]
        rate3 = listOfTuples[2][1]
        rate4 = listOfTuples[3][1]
        rate5 = listOfTuples[4][1]


    #GET TF-IDF PREGENERATED MATRIX
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    nameIngredients = []  # to store all names of features...previously stored
    nameDishes = [] #to store all names of dishes of the menu

    tfIdfIngrNames, tfIdfDishesNames, tfIdfMenu = returnFilesNamesByMacroCateg(usersGlobalVariables[str(update.callback_query.from_user.id)]["userChoiceMacroCategoryGlobal"])

    with open(tfIdfIngrNames) as file:
        nameIngredients = file.read().splitlines()
    with open(tfIdfDishesNames) as file:
        nameDishes = file.read().splitlines()

    #Get matrix tfidf previously performed and make a dataframe with cols FEATURES and index NAMEDISHES
    import csv
    import numpy
    matrix = numpy.array(list(csv.reader(open(tfIdfMenu, "rt"), delimiter=","))).astype("float")
    df = pd.DataFrame(matrix, columns=nameIngredients, index=nameDishes)


    # HOW TO BUILD THE USER PROFILE:
    #  extract vectors of somministrated dishes and perform a weighted average
    #  FORMULA   --->   (R1 * tfidf1 + R2 * tfid2 + R3 * tfidf3 + R4 * tfidf4 + R5 * tfidf5) / (R1+R2+R3+R4+R5)
    #  LEGEND    --->    tfidfX = vector of dish somministrated   RX = rate of user for that dish
    #
    # example
    #            f1    f2     f3   ...
    # tfidf1     0.3   0.4    1
    # tfidf2     0.4   0.2    0.8
    # tfidf3     0.2   0.4    1
    # tfidf4     0.5   0.3    0.7
    # tfidf5     0.2   0.2    1

    #*************NOW RATES ARE ALL 5 (USER LIKED A DISH -> RATE = 5)**************
    # rates = 5,5,5,5,5
    # 5*[0.3 0.4 0.2] + 5*[0.4 0.2 0.4] + 5*[1 0.8 1] = [1.2 1.6 ...] + ..... /(5+5+5+5+5)= we obtain a new vector
    # output = user profile vector

    start,finish = returnIndexesByMacroCateg(usersGlobalVariables[str(update.callback_query.from_user.id)]["userChoiceMacroCategoryGlobal"])

    if usersGlobalVariables[str(update.callback_query.from_user.id)]["flagEmergencyRecommendation"] is True:
        if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 4:
            tfidf1 = df.values[listOfTuples[0][0] - start]
            tfidf2 = df.values[listOfTuples[1][0] - start]
            tfidf3 = df.values[listOfTuples[2][0] - start]
            tfidf4 = df.values[listOfTuples[3][0] - start]
            tfidf1 = tfidf1 * rate1
            tfidf2 = tfidf2 * rate2
            tfidf3 = tfidf3 * rate3
            tfidf4 = tfidf4 * rate4
            sumList = [a + b + c + d  for a, b, c, d in zip(tfidf1, tfidf2, tfidf3, tfidf4)]
            weightAvg = [elem / sum(usersGlobalVariables[str(update.callback_query.from_user.id)]["userRates"]) for elem in sumList]
            userProfile = weightAvg
            usersGlobalVariables[str(update.callback_query.from_user.id)]["userProfileIngrAndScores"] = list(zip(nameIngredients, userProfile))
            fiveDishes = [listOfTuples[0][0] - start, listOfTuples[1][0] - start, listOfTuples[2][0] - start, listOfTuples[3][0] - start]  # list containing the index of somministrated dishes
            updatedDf = df.drop(df.index[[fiveDishes[0], fiveDishes[1], fiveDishes[2], fiveDishes[3]]])
        elif usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 3:
            tfidf1 = df.values[listOfTuples[0][0] - start]
            tfidf2 = df.values[listOfTuples[1][0] - start]
            tfidf3 = df.values[listOfTuples[2][0] - start]
            tfidf1 = tfidf1 * rate1
            tfidf2 = tfidf2 * rate2
            tfidf3 = tfidf3 * rate3
            sumList = [a + b + c  for a, b, c in zip(tfidf1, tfidf2, tfidf3)]
            weightAvg = [elem / sum(usersGlobalVariables[str(update.callback_query.from_user.id)]["userRates"]) for elem in sumList]
            userProfile = weightAvg
            usersGlobalVariables[str(update.callback_query.from_user.id)]["userProfileIngrAndScores"] = list(zip(nameIngredients, userProfile))
            fiveDishes = [listOfTuples[0][0] - start, listOfTuples[1][0] - start, listOfTuples[2][0] - start]  # list containing the index of somministrated dishes
            updatedDf = df.drop(df.index[[fiveDishes[0], fiveDishes[1], fiveDishes[2]]])
        elif usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 2:
            tfidf1 = df.values[listOfTuples[0][0] - start]
            tfidf2 = df.values[listOfTuples[1][0] - start]
            tfidf1 = tfidf1 * rate1
            tfidf2 = tfidf2 * rate2
            sumList = [a + b for a, b in zip(tfidf1, tfidf2)]
            weightAvg = [elem / sum(usersGlobalVariables[str(update.callback_query.from_user.id)]["userRates"]) for elem in sumList]
            userProfile = weightAvg
            usersGlobalVariables[str(update.callback_query.from_user.id)]["userProfileIngrAndScores"] = list(zip(nameIngredients, userProfile))
            fiveDishes = [listOfTuples[0][0] - start, listOfTuples[1][0] - start]  # list containing the index of somministrated dishes
            updatedDf = df.drop(df.index[[fiveDishes[0], fiveDishes[1]]])
        elif usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 1:
            tfidf1 = df.values[listOfTuples[0][0] - start]
            tfidf1 = tfidf1 * rate1
            userProfile = tfidf1
            usersGlobalVariables[str(update.callback_query.from_user.id)]["userProfileIngrAndScores"] = list(zip(nameIngredients, userProfile))
            fiveDishes = [listOfTuples[0][0] - start]  # list containing the index of somministrated dishes
            updatedDf = df.drop(df.index[[fiveDishes[0]]])
    else:
        tfidf1 = df.values[listOfTuples[0][0]-start]
        tfidf2 = df.values[listOfTuples[1][0]-start]
        tfidf3 = df.values[listOfTuples[2][0]-start]
        tfidf4 = df.values[listOfTuples[3][0]-start]
        tfidf5 = df.values[listOfTuples[4][0]-start]
        tfidf1 = tfidf1 * rate1
        tfidf2 = tfidf2 * rate2
        tfidf3 = tfidf3 * rate3
        tfidf4 = tfidf4 * rate4
        tfidf5 = tfidf5 * rate5
        sumList = [a + b + c + d + e for a, b, c, d, e in zip(tfidf1, tfidf2, tfidf3, tfidf4, tfidf5)]
        weightAvg = [elem / sum(usersGlobalVariables[str(update.callback_query.from_user.id)]["userRates"]) for elem in sumList]

        userProfile = weightAvg

        #Store in a global var the dict ingrNameUssProfile:score
        usersGlobalVariables[str(update.callback_query.from_user.id)]["userProfileIngrAndScores"] = list(zip(nameIngredients, userProfile))

        #[111, 321, 7, 295, 322]
        fiveDishes = [listOfTuples[0][0]-start,listOfTuples[1][0]-start,listOfTuples[2][0]-start,listOfTuples[3][0]-start,listOfTuples[4][0]-start]#list containing the index of somministrated dishes

        #def checkIfDuplicates_1(listOfElems):
        #    ''' Check if given list contains any duplicates '''
        #    if len(listOfElems) == len(set(listOfElems)):
        #        return False
        #    else:
        #        return True

        #print("Check for duplicates, this created problems in the past", checkIfDuplicates_1(list(df.index)))


        # Removed the 5 rows from the dataframe of item profiles
        updatedDf = df.drop(df.index[[fiveDishes[0], fiveDishes[1], fiveDishes[2], fiveDishes[3],fiveDishes[4]]])



    # Create user profile dataframe
    userProfileDf = pd.DataFrame([userProfile], columns=nameIngredients, index=["User profile"])

    # Add user profile to item profiles dataframe in order to compute the cosine similarity
    if not userProfileDf.empty:
        updatedDf2 = pd.concat([updatedDf, userProfileDf])
    else:
        updatedDf2 = updatedDf.append(pd.DataFrame([userProfile],columns=nameIngredients),ignore_index=True)
        if updatedDf2.empty:
            # A series object with the same index as DataFrame
            updatedDf2 = updatedDf.append(pd.Series(userProfile, index=nameIngredients),ignore_index=True)

    # Perform cosine similarity
    cosineSim = cosine_similarity(updatedDf2)


    # recommendation list to be generated
    recommendation = []

    if usersGlobalVariables[str(update.callback_query.from_user.id)]["flagEmergencyRecommendation"] is True:
        if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 4:
            usProfCosSimItemProf = cosineSim[496]
        if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 3:
            usProfCosSimItemProf = cosineSim[497]
        if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 2:
            usProfCosSimItemProf = cosineSim[498]
        if usersGlobalVariables[str(update.callback_query.from_user.id)]["numberLikes"] == 1:
            usProfCosSimItemProf = cosineSim[499]
    else:
        # get last row (the user profile cos sim with other rows ... NB we have removed X (1 up to 5) rows -> -numeroLikes
        usProfCosSimItemProf = cosineSim[495]  #-numeroLikes get the last row of cosine similarity matrix: compared user profile with all other item profiles

    # create a list that matches name of dishes and cosine similarity weight
    for name, cosine in zip(updatedDf2.index, usProfCosSimItemProf):
        recommendation.append((name, cosine))

    recommendation.pop()  # remove the last element (the one representing the user profile = 1)

    #we obtain a list of dishes with cosine similarity scores THAT SHOULD BE SORTED BY DECREASING ORDER OF THE SCORES

    #SCAN RECOMMENDATION LIST TO REMOVE DISHES THAT ARE NOT PREESENT IN MENUAFTER CONSTRAINTS (BECAUSE WE USE THE TFIDF MATRIX PREGENERATED
    #IT'S MORE EFFICIENT INSTEAD OF PERFORMING IT EVERYTIME...Scan reversed recommendation list and remove disehs (we have already the finished recommendation list to be shown)

    #Rare problem: the recommendation list is empty (SEE DOWN)


    #_____________________SECTION USEFUL FOR RECOMMENDATION EXPLANATION____________________________________


    import numpy as np

    # Sort by score
    sortedIngrAndScoreList = sorted(usersGlobalVariables[str(update.callback_query.from_user.id)]["userProfileIngrAndScores"], key=lambda x: x[1], reverse=True)

    # Define a threshold for recommendation explanation step AS average of TfIdf scores
    tresholdTfIdf = np.average([x[1] for x in usersGlobalVariables[str(update.callback_query.from_user.id)]["userProfileIngrAndScores"]])

    # get top n features of tf idf that are over the treshold! (later check the ones that are in the dish)
    ingrTfIdfOverTreshold = [elem[0] for elem in sortedIngrAndScoreList if elem[1] >= tresholdTfIdf]

    #global ingrTfIdfOverTresholdWithSpaces
    usersGlobalVariables[str(update.callback_query.from_user.id)]["ingrTfIdfOverTresholdWithSpaces"] = [getNameWithSpaces(elem, usersGlobalVariables[str(update.callback_query.from_user.id)]["userChoiceMacroCategoryGlobal"]) for elem in ingrTfIdfOverTreshold]

    #____________________________________________ END ______________________________________________________


    nomiDishes = returnNamesDishMenuAfterConstr(macroCategNames[usersGlobalVariables[str(update.callback_query.from_user.id)]["userChoiceMacroCategoryGlobal"]],update)

    recommendation = [elem for elem in recommendation if elem[0] in nomiDishes]

    #Sort recommendation list by cosine scores
    recommendation.sort(key=lambda y: y[1], reverse=True)



    #propose a dish (first of recomm list generated......)
    #now use fitered menu obtained with intol check ::incaseskipintolstartfromstartmenu:: and ingr scores obtained by scen 1 3       
    #menuAfterConstraintsCheck in ogni caso usare questa var

    if len(recommendation) == 0:
        print("(ERROR 5) END OF MENU for user ", str(update.message.from_user.id))
        update.message.reply_text('Sorry...I do not have any food recommendation for you')

        #update.message.reply_text('Please send us an email. We will help you completing the task in the available time. \nFollow the link in the Amazon MTurk HIT instructions:')
        #context.bot.send_video(chat_id=update.message.chat_id, video=open('images/support_video.mov', 'rb'),height=1288, width=2346, supports_streaming=True, timeout=20,caption="Support instructions")

        del usersGlobalVariables[str(update.message.from_user.id)]
        return ConversationHandler.END


    #REALLY IMPORTANT STEP

    #function that turn the list of (name,cosine) in a list of sorted (same order) corresponding Piatto objects

    #RECOMMENDATION LIST (SORTED FROM THE MOST SIMILAR DISH TO USER PROFILE)
    usersGlobalVariables[str(update.callback_query.from_user.id)]["recommendationObjectList"] = turnToupleNameCosineListIntoObjectsList(recommendation)

    #RECOMMENDATION LIST SORTED USING FSA SCORE (SORTED FROM THE HEALTHIEST DISH)
    usersGlobalVariables[str(update.callback_query.from_user.id)]["recommendationObjectListSortedFSA"] = sortByFSA(usersGlobalVariables[str(update.callback_query.from_user.id)]["recommendationObjectList"])


    #Show the first dish of the rec list
    usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"] = usersGlobalVariables[str(update.callback_query.from_user.id)]["recommendationObjectList"][0]
    
    raccNome = 'I think you would like this dish: '+usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].nome
    update.effective_message.reply_text(raccNome, reply_markup=ReplyKeyboardRemove())
    usersGlobalVariables[str(update.callback_query.from_user.id)]["startPresentationDate"] = update.effective_message.date
    # Find the most similar dish to the proposed one and at the same time the healthiest
    mostSimAndHeal = findMostSimilarAndHealthiest(usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"], update)

    usersGlobalVariables[str(update.callback_query.from_user.id)]["listaDishesPairwiseRecommendation"] =[]
    usersGlobalVariables[str(update.callback_query.from_user.id)]["listaDishesPairwiseRecommendation"].append(tuple((usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].idDishUrl,mostSimAndHeal.idDishUrl)))

    if usersGlobalVariables[str(update.callback_query.from_user.id)]["flagTextualVisualChoice"] == True:

        # NEW
        if usersGlobalVariables[str(update.callback_query.from_user.id)]["userChoiceModalityGlobal"] == 'Rate dish proposal (visual+label explan) ✅':
            # SCEN 4 multi-modal (dish name + image + label for expl) or MMLAB
            update.effective_message.reply_media_group(media=[InputMediaPhoto(usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].immagine),InputMediaPhoto(open("/home/giocast/prototypeMMCISnorway5MAY/" + str(usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].FSAlabel), 'rb'))])
            raccHealthierNome = 'But I also propose to you a healthier alternative: ' + mostSimAndHeal.nome  # BUT I PROPOSE YOU ALSO AN HEARTIER ALTERNATIVE
            update.effective_message.reply_text(raccHealthierNome, reply_markup=ReplyKeyboardRemove())
            update.effective_message.reply_media_group([InputMediaPhoto(mostSimAndHeal.immagine),InputMediaPhoto(open("/home/giocast/prototypeMMCISnorway5MAY/" + str(mostSimAndHeal.FSAlabel), 'rb'))])
        else:
            # SCEN 3 - multi-modal (dish name + image) or MM
            raccHealthierNome = 'But I also propose to you a healthier alternative: ' + mostSimAndHeal.nome  # BUT I PROPOSE YOU ALSO AN HEARTIER ALTERNATIVE
            update.effective_message.reply_text(raccHealthierNome, reply_markup=ReplyKeyboardRemove())

            # OLD IMP WORKS update.message.reply_photo(usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].immagine)

            # Reply the 2 images pairwise o let the user see the visual comparison
            update.effective_message.reply_media_group([InputMediaPhoto(usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].immagine),InputMediaPhoto(mostSimAndHeal.immagine)])




    else:
        #Case Textual or T
        #BUT I PROPOSE YOU ALSO AN HEARTIER ALTERNATIVE
        raccHealthierNome = 'But I also propose to you a healthier alternative: ' + mostSimAndHeal.nome
        update.effective_message.reply_text(raccHealthierNome, reply_markup=ReplyKeyboardRemove())


    #_______________________________RECOMMENDATION EXPLANATION______________________

    if usersGlobalVariables[str(update.callback_query.from_user.id)]["flagSkippedAl"] == False or usersGlobalVariables[str(update.callback_query.from_user.id)]["boolFirstConstr"] == True:
        messDis = 'I reccomend these ' + str(macroCategNames[usersGlobalVariables[str(update.callback_query.from_user.id)]["userChoiceMacroCategoryGlobal"]]).lower() + ' dishes because I know that you have diet constraints due to: ' + ", ".join([x.lower() for x in usersGlobalVariables[str(update.callback_query.from_user.id)]["memoryConstraints"]])
        update.effective_message.reply_text(messDis)
    else:
        macr = 'I recommend these dishes because I know that you are searching for ' + str(macroCategNames[usersGlobalVariables[str(update.callback_query.from_user.id)]["userChoiceMacroCategoryGlobal"]]).lower()
        update.effective_message.reply_text(macr)

    listIngrToShow = []
    for elem in usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].ingredienti:
        if elem in usersGlobalVariables[str(update.callback_query.from_user.id)]["ingrTfIdfOverTresholdWithSpaces"]:
            listIngrToShow.append(elem)

    if len(listIngrToShow) > 0:
        messIngrLiked = 'The first dish I proposed contains ingredients that you might like: ' + ", ".join([x.lower() for x in listIngrToShow])
        update.effective_message.reply_text(messIngrLiked)

    # numero, nome, ingredienti, immagine, calorie, macroCategoria, servings, totalGramWeight, protein100, carb100, fiber100, sugar100, fat100, satfat100, salt100, kj100, nutri_score, FSAscore, FSAlabel

    if usersGlobalVariables[str(update.callback_query.from_user.id)]["userChoiceModalityGlobal"] == 'Rate dish proposal (visual+label explan) ✅':
        # SCEN 4 - multi-modal (dish name + image + label for explan)

        update.effective_message.reply_text("You can look at the nutritional labels of first and second dish!",reply_markup=ReplyKeyboardRemove())
    else:
        kcalA = usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].calorie
        kjA = usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].kj100
        sugarA = usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].sugar100
        fatA = usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].fat100
        satfatA = usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].satfat100
        saltA = usersGlobalVariables[str(update.callback_query.from_user.id)]["dishToRecommend"].salt100

        kcalB = mostSimAndHeal.calorie
        kjB = mostSimAndHeal.kj100
        sugarB = mostSimAndHeal.sugar100
        fatB = mostSimAndHeal.fat100
        satfatB = mostSimAndHeal.satfat100
        saltB = mostSimAndHeal.salt100

        messHealthExplanation = 'The second dish I proposed has: \n';
        initLen = len(messHealthExplanation)

        if int(kcalB) < int(kcalA):
            messHealthExplanation+='• less calories (' + kcalB + ' Kcal) than the first one (' + kcalA + ' Kcal) \n'
        if float(sugarB) < float(sugarA):
            messHealthExplanation += '• less sugars than the first one \n'
        if float(fatB) < float(fatA):
            messHealthExplanation += '• less fats than the first one \n'
        if float(satfatB) < float(satfatA):
            messHealthExplanation += '• less saturated fats than the first one \n'
        if float(saltB) < float(saltA):
            messHealthExplanation += '• less salt than the first one \n'

        if len(messHealthExplanation) > initLen:
            update.effective_message.reply_text(messHealthExplanation)

    usersGlobalVariables[str(update.callback_query.from_user.id)]["tempHealthyAlternative"] = mostSimAndHeal

    #__________________________________ END _______________________________________
    
    reply_keyboard = [['I like first dish'], ['I like second dish'], ['I want something different...']]
    update.effective_message.reply_text('What do you think about my recommendations?',reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return AFTERRECOMMENDATION


#FUNC: sorts the recommendation list by FSA score

def sortByFSA(recList):
    listSortByFSA = recList.copy()
    #Sort recommendation list based on FSA score!
    listSortByFSA.sort(key=lambda x: int(x.FSAscore), reverse=False)
    return listSortByFSA


#FUNC: finds the best item in terms of healthiness and similarity to the actual dish of recommendation list presented to the user

def findMostSimilarAndHealthiest(dishToRecommend,update):
    listaSortFSA = usersGlobalVariables[str(update.callback_query.from_user.id)]["recommendationObjectListSortedFSA"]
    listaRec = usersGlobalVariables[str(update.callback_query.from_user.id)]["recommendationObjectList"]

    indexDishToRecommend = listaRec.index(dishToRecommend)

    tupleIndexes = []

    nElem = len(listaRec)
    # start by NEXT ELEMENT
    for idx in range(indexDishToRecommend+1,nElem):
        elem = listaRec[idx]
        #Valutare di rimuovere elementi considerati PER EVITARE RIDONDANZA, RISCHIO STESSI VALORI
        simInd = listaRec.index(elem)
        healInd = listaSortFSA.index(elem)
        avg = 0.4*simInd + 0.6*healInd
        tupleIndexes.append((elem,avg))

    healthierAlternative = min(tupleIndexes,key = lambda x: x[1])
    return healthierAlternative[0]
def findMostSimilarAndHealthiestCopy(dishToRecommend,update):
    listaSortFSA = usersGlobalVariables[str(update.message.from_user.id)]["recommendationObjectListSortedFSA"]
    listaRec = usersGlobalVariables[str(update.message.from_user.id)]["recommendationObjectList"]

    indexDishToRecommend = listaRec.index(dishToRecommend)

    tupleIndexes = []

    nElem = len(listaRec)
    # start by NEXT ELEMENT
    for idx in range(indexDishToRecommend+1,nElem):
        elem = listaRec[idx]
        #Valutare di rimuovere elementi considerati PER EVITARE RIDONDANZA, RISCHIO STESSI VALORI
        simInd = listaRec.index(elem)
        healInd = listaSortFSA.index(elem)
        avg = 0.4*simInd + 0.6*healInd
        tupleIndexes.append((elem,avg))

    healthierAlternative = min(tupleIndexes,key = lambda x: x[1])
    return healthierAlternative[0]


#FUNC: return image of dish given its name
def getImgByName(name):
    for elem in menu:
        if elem.nome == name:
            return elem.immagine


#FUNC: return list of names of menuafterconstraints elements
def returnNamesDishMenuAfterConstr(macroCateg,update):
    lista = []

    for elem in usersGlobalVariables[str(update.callback_query.from_user.id)]["menuAfterConstraintsCheck"]:
        if elem.macroCategoria == macroCateg:
            lista.append(elem.nome)

    return lista


#FUNC: return ojects given name and cosine

def turnToupleNameCosineListIntoObjectsList(lista):
    objectsList = []
    #lista is the sorted list of dishes based on the cosine similarity score
    for name, cosine in lista:
        for elem in menu:
            if name == elem.nome:
                objectsList.append(elem)

    #if(len(objectsList)==len(lista)):
    #   print("ITS OK: correctly turned list of touples (name,cos) in list ob objects")
    return objectsList


#FUNC: return name of igredients with space

def getNameWithSpaces(name, macroCateg):

    if macroCateg == "Pasta 🍝":
        categFile = "allIngrPasta500Spaces.txt"
    elif macroCateg == "Salad 🥗":
        categFile = "allIngrSalad500Spaces.txt"
    elif macroCateg == "Dessert 🧁":
        categFile = "allIngrDessert500Spaces.txt"
    elif macroCateg == "Snack 🍟":
        categFile = "allIngrSnack500Spaces.txt"

    lista = []
    with open(categFile) as file:
        nameIngredients = file.read().splitlines()
        lista = [(elem,similar(name,elem)) for elem in nameIngredients]
        listaSorted = sorted(lista, key=lambda x: x[1], reverse=True)

    return listaSorted[0][0]


#*FUNC: function of the chatbot flow -> iterate on user decision after the recommendation (prefer first, second, or want something else -> iteration)

def afterRecommendation(update: Update, context: CallbackContext) -> int:
    global usersGlobalVariables
    userResponse = update.message.text

    usersGlobalVariables[str(update.message.from_user.id)]["counterInteractionTurns"] = usersGlobalVariables[str(update.message.from_user.id)]["counterInteractionTurns"] + 1

    if userResponse == 'I like first dish':

        usersGlobalVariables[str(update.message.from_user.id)]["userFinalChoiceDish"] = usersGlobalVariables[str(update.message.from_user.id)]["recommendationObjectList"][usersGlobalVariables[str(update.message.from_user.id)]["nextInd"]]
        usersGlobalVariables[str(update.message.from_user.id)]["finalDishNotChosen"] = usersGlobalVariables[str(update.message.from_user.id)]["tempHealthyAlternative"].idDishUrl
        usersGlobalVariables[str(update.message.from_user.id)]["isUserFinalChoiceHealthy"] = False
        usersGlobalVariables[str(update.message.from_user.id)]["finishPresentationDate"] = update.message.date

        update.message.reply_text('Thanks you for using this bot!', reply_markup=ReplyKeyboardRemove())

        reply_keyboard = [['1️⃣'], ['2️⃣'], ['3️⃣'], ['4️⃣'], ['5️⃣']]
        update.message.reply_text('Please rate our service! Then you will receive a code',reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return FINALRATINGS       

    elif userResponse == 'I like second dish':

        usersGlobalVariables[str(update.message.from_user.id)]["userFinalChoiceDish"] = usersGlobalVariables[str(update.message.from_user.id)]["tempHealthyAlternative"]
        usersGlobalVariables[str(update.message.from_user.id)]["finalDishNotChosen"] = usersGlobalVariables[str(update.message.from_user.id)]["recommendationObjectList"][usersGlobalVariables[str(update.message.from_user.id)]["nextInd"]].idDishUrl
        usersGlobalVariables[str(update.message.from_user.id)]["isUserFinalChoiceHealthy"] = True
        usersGlobalVariables[str(update.message.from_user.id)]["finishPresentationDate"] = update.message.date

        update.message.reply_text('Thanks you for using this bot!', reply_markup=ReplyKeyboardRemove())

        reply_keyboard = [['1️⃣'], ['2️⃣'], ['3️⃣'], ['4️⃣'], ['5️⃣']]
        update.message.reply_text('Please rate our service! Then you will receive a code',reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return FINALRATINGS

    elif userResponse == 'I want something different...':
        usersGlobalVariables[str(update.message.from_user.id)]["nextInd"]+=1
        if usersGlobalVariables[str(update.message.from_user.id)]["nextInd"] < len(usersGlobalVariables[str(update.message.from_user.id)]["recommendationObjectList"])-1:


            usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"] =  usersGlobalVariables[str(update.message.from_user.id)]["recommendationObjectList"][usersGlobalVariables[str(update.message.from_user.id)]["nextInd"]]

            raccNome = 'I think you would like ' + usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].nome
            update.message.reply_text(raccNome, reply_markup=ReplyKeyboardRemove())

            # Find the most similar dish to the proposed one and at the same time the healthiest
            mostSimAndHeal = findMostSimilarAndHealthiestCopy(usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"], update)

            usersGlobalVariables[str(update.message.from_user.id)]["listaDishesPairwiseRecommendation"].append(tuple((usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].idDishUrl,mostSimAndHeal.idDishUrl)))

            if usersGlobalVariables[str(update.message.from_user.id)]["flagTextualVisualChoice"] == True:

                if usersGlobalVariables[str(update.message.from_user.id)]["userChoiceModalityGlobal"] == 'Rate dish proposal (visual+label explan) ✅':
                    # SCEN 4 multi-modal (dish name + image + label for expl) or MMLAB
                    update.message.reply_media_group(media=[InputMediaPhoto(usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].immagine),InputMediaPhoto(open("/home/giocast/prototypeMMCISnorway5MAY/" + str(usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].FSAlabel), 'rb'))])
                    raccHealthierNome = 'But I also propose to you a healthier alternative: ' + mostSimAndHeal.nome  # BUT I PROPOSE YOU ALSO AN HEARTIER ALTERNATIVE
                    update.message.reply_text(raccHealthierNome, reply_markup=ReplyKeyboardRemove())
                    update.message.reply_media_group([InputMediaPhoto(mostSimAndHeal.immagine), InputMediaPhoto(open("/home/giocast/prototypeMMCISnorway5MAY/" + str(mostSimAndHeal.FSAlabel), 'rb'))])
                else:
                    # SCEN 3 - multi-modal (dish name + image) or MM
                    raccHealthierNome = 'But I also propose to you a healthier alternative: ' + mostSimAndHeal.nome  # BUT I PROPOSE YOU ALSO AN HEARTIER ALTERNATIVE
                    update.message.reply_text(raccHealthierNome, reply_markup=ReplyKeyboardRemove())

                    # Reply the 2 images pairwise o let the user see the visual comparison
                    update.message.reply_media_group([InputMediaPhoto(usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].immagine),InputMediaPhoto(mostSimAndHeal.immagine)])


            else:
                # Textual or T
                # BUT I PROPOSE YOU ALSO AN HEARTIER ALTERNATIVE
                raccHealthierNome = 'But I also propose to you a healthier alternative: ' + mostSimAndHeal.nome
                update.message.reply_text(raccHealthierNome, reply_markup=ReplyKeyboardRemove())



            # _______________________________RECOMMENDATION EXPLANATION______________________

            if usersGlobalVariables[str(update.message.from_user.id)]["flagSkippedAl"] == False or usersGlobalVariables[str(update.message.from_user.id)]["boolFirstConstr"] == True:
                messDis = 'I reccomend these ' + str(macroCategNames[usersGlobalVariables[str(update.message.from_user.id)]["userChoiceMacroCategoryGlobal"]]).lower() + ' dishes because I know that you have diet constraints due to: ' + ", ".join([x.lower() for x in usersGlobalVariables[str(update.message.from_user.id)]["memoryConstraints"]])
                update.message.reply_text(messDis)
            else:
                macr = 'I recommend these dishes because I know that you are searching for ' + str(macroCategNames[usersGlobalVariables[str(update.message.from_user.id)]["userChoiceMacroCategoryGlobal"]]).lower()
                update.message.reply_text(macr)

            listIngrToShow = []
            for elem in usersGlobalVariables[str(update.message.from_user.id)]["recommendationObjectList"][usersGlobalVariables[str(update.message.from_user.id)]["nextInd"]].ingredienti:
                if elem in usersGlobalVariables[str(update.message.from_user.id)]["ingrTfIdfOverTresholdWithSpaces"]:
                    listIngrToShow.append(elem)

            if len(listIngrToShow) > 0:
                messIngrLiked = 'The first dish I proposed contains ingredients that you might like: ' + ", ".join([x.lower() for x in listIngrToShow])
                update.message.reply_text(messIngrLiked)

            # numero, nome, ingredienti, immagine, calorie, macroCategoria, servings, totalGramWeight, protein100, carb100, fiber100, sugar100, fat100, satfat100, salt100, kj100, nutri_score, FSAscore, FSAlabel

            if usersGlobalVariables[str(update.message.from_user.id)]["userChoiceModalityGlobal"] == 'Rate dish proposal (visual+label explan) ✅':
                # SCEN 4 - multi-modal (dish name + image + label for explan)
                update.message.reply_text("You can look at the nutritional labels of first and second dish!",reply_markup=ReplyKeyboardRemove())
            else:
                kcalA = usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].calorie
                kjA = usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].kj100
                sugarA = usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].sugar100
                fatA = usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].fat100
                satfatA = usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].satfat100
                saltA = usersGlobalVariables[str(update.message.from_user.id)]["dishToRecommend"].salt100

                kcalB = mostSimAndHeal.calorie
                kjB = mostSimAndHeal.kj100
                sugarB = mostSimAndHeal.sugar100
                fatB = mostSimAndHeal.fat100
                satfatB = mostSimAndHeal.satfat100
                saltB = mostSimAndHeal.salt100

                messHealthExplanation = 'The second dish I proposed has: \n';
                initLen = len(messHealthExplanation)

                if int(kcalB) < int(kcalA):
                    messHealthExplanation += '• less calories (' + kcalB + ' Kcal) than the first one (' + kcalA + ' Kcal) \n'
                if float(sugarB) < float(sugarA):
                    messHealthExplanation += '• less sugars than the first one \n'
                if float(fatB) < float(fatA):
                    messHealthExplanation += '• less fats than the first one \n'
                if float(satfatB) < float(satfatA):
                    messHealthExplanation += '• less saturated fats than the first one \n'
                if float(saltB) < float(saltA):
                    messHealthExplanation += '• less salt than the first one \n'

                if len(messHealthExplanation) > initLen:
                    update.message.reply_text(messHealthExplanation)

            usersGlobalVariables[str(update.message.from_user.id)]["tempHealthyAlternative"] = mostSimAndHeal

            # __________________________________ END _______________________________________

            reply_keyboard = [['I like first dish'], ['I like second dish'], ['I want something different...']]
            update.message.reply_text('What do you think about my recommendations?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

            return AFTERRECOMMENDATION
        else:
            print("(ERROR 6) EXCEED IN ASKING FOR SOMETHING DIFFERENT for user ", str(update.message.from_user.id))
            update.message.reply_text('Sorry...I do not have more recommendation for you')
            usersGlobalVariables[str(update.message.from_user.id)]["userFinalChoiceDish"] = None
            usersGlobalVariables[str(update.message.from_user.id)]["isUserFinalChoiceHealthy"] = None
            update.message.reply_text('Thanks you for using this bot!', reply_markup=ReplyKeyboardRemove())

            reply_keyboard = [['1️⃣'], ['2️⃣'], ['3️⃣'], ['4️⃣'], ['5️⃣']]
            update.message.reply_text('Please rate our service! Then you will receive a code',reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            print("going to final ratings")
            return FINALRATINGS


#FUNC: skip function handler

def skipSendingImages(update: Update, context: CallbackContext) -> int:

    global usersGlobalVariables
    usersGlobalVariables[str(update.message.from_user.id)]["flagCheckGotFirstBranch2"] = False
    usersGlobalVariables[str(update.message.from_user.id)]["flagSkipped"] = True

    processing(update, context)  #INFO: effettivamente, non chiedo testoin questa fase: struttura a stati non funzionerebbe
    return 0


#*FUNC: function of the chatbot flow -> cancel conversation

def cancel(update: Update, context: CallbackContext):
    """Cancels and ends the conversation."""
    user = update.message.from_user

    logger.info("User %s canceled the conversation.", user.id)

    if "mTurkCode" in usersGlobalVariables[str(update.message.from_user.id)]:
        update.message.reply_text('Bye! I hope we can talk again some day 😁 \nHere your unique code: ',reply_markup=ReplyKeyboardRemove())
        update.message.reply_text(usersGlobalVariables[str(update.message.from_user.id)]["mTurkCode"])
        update.message.reply_text('Please paste it in MTurk text input to get paid!')
    else:
        update.message.reply_text('Bye! I hope we can talk again some day 😁 ', reply_markup=ReplyKeyboardRemove())

    del usersGlobalVariables[str(update.message.from_user.id)]
    return ConversationHandler.END


#*FUNC: function of the chatbot flow -> ask for rating the service

def ratings(update: Update, context: CallbackContext) -> int:
    
    update.message.reply_text('Thanks you for using this bot!', reply_markup=ReplyKeyboardRemove())

    reply_keyboard = [['1️⃣'], ['2️⃣'], ['3️⃣'], ['4️⃣'], ['5️⃣']]
    update.message.reply_text('Please rate our service! Then you will receive a code', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return FINALRATINGS


def get_random_string():
    import random
    import string
    # choose from all lowercase letter
    length = 6
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


#*FUNC: function of the chatbot flow -> process all the information to store after the experiment

def finalRatings(update: Update, context: CallbackContext) -> int:

    global usersGlobalVariables

    usersGlobalVariables[str(update.message.from_user.id)]["counterInteractionTurns"] = usersGlobalVariables[str(update.message.from_user.id)]["counterInteractionTurns"] + 1

    scenario = ''
    tinyScenario = ''

    if usersGlobalVariables[str(update.message.from_user.id)]["firstUserChoice"] == 'Send your pictures 📸':
        scenario = 'Scenario 2'
    elif usersGlobalVariables[str(update.message.from_user.id)]["firstUserChoice"] == 'Rate dish proposals (textual) ⭐️📝':
        scenario = 'Scenario Textual' #'Scenario 1'
        tinyScenario = 'TEXT'
    elif usersGlobalVariables[str(update.message.from_user.id)]["firstUserChoice"] == 'Rate dish proposals (visual) ⭐️🍝':
        scenario = 'Scenario Multi-modal (Text + Image)' #'Scenario 3'
        tinyScenario = 'MM'
    elif usersGlobalVariables[str(update.message.from_user.id)]["firstUserChoice"] == 'Rate dish proposal (visual+label explan) ✅':
        scenario = 'Scenario Multi-modal (Text + Image + Label expl.)' #'Scenario 4'
        tinyScenario = 'MMLAB'

    # Scenario 1 - 5 stars
    rateUser = update.message.text

    usersGlobalVariables[str(update.message.from_user.id)]["finishSessionDate"] = update.message.date


    from datetime import datetime
    #new_dt = dt_string[:19] TO REMOVE +00:00
    dataFine = datetime.strptime(str(usersGlobalVariables[str(update.message.from_user.id)]["finishSessionDate"])[:19],'%Y-%m-%d %H:%M:%S')
    dataInizio = datetime.strptime(str(usersGlobalVariables[str(update.message.from_user.id)]["startSessionDate"])[:19],'%Y-%m-%d %H:%M:%S')

    dataInizioPrefElic = datetime.strptime(str(usersGlobalVariables[str(update.message.from_user.id)]["startPreferenceElicitationDate"])[:19],'%Y-%m-%d %H:%M:%S')
    dataFinePrefElic = datetime.strptime(str(usersGlobalVariables[str(update.message.from_user.id)]["finishPreferenceElicitationDate"])[:19],'%Y-%m-%d %H:%M:%S')

    dataInizioPresentation = datetime.strptime(str(usersGlobalVariables[str(update.message.from_user.id)]["startPresentationDate"])[:19],'%Y-%m-%d %H:%M:%S')
    dataFinePresentation = datetime.strptime(str(usersGlobalVariables[str(update.message.from_user.id)]["finishPresentationDate"])[:19], '%Y-%m-%d %H:%M:%S')

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    durataConversazione = int((dataFine - dataInizio).total_seconds())
    durataInteraction = int((dataFinePrefElic - dataInizioPrefElic).total_seconds())
    durataPresentation = int((dataFinePresentation - dataInizioPresentation).total_seconds())

    healthyChoice = usersGlobalVariables[str(update.message.from_user.id)]["isUserFinalChoiceHealthy"]

    if healthyChoice is not None:
        healthinessPreferredDishNutri = usersGlobalVariables[str(update.message.from_user.id)]["userFinalChoiceDish"].nutriScore
        healthinessPreferredDishFSA = usersGlobalVariables[str(update.message.from_user.id)]["userFinalChoiceDish"].FSAscore
    else:
        healthinessPreferredDishNutri = None
        healthinessPreferredDishFSA = None

    if healthyChoice is not None:
        idPreferredDish = usersGlobalVariables[str(update.message.from_user.id)]["userFinalChoiceDish"].idDishUrl
    else:
        idPreferredDish = None

    lineaDaInserire = []

    rateUserToSys = ''

    if rateUser == '1️⃣':
        rateUserToSys = '1'
    elif rateUser == '2️⃣':
        rateUserToSys = '2'
    elif rateUser == '3️⃣':
        rateUserToSys = '3'
    elif rateUser == '4️⃣':
        rateUserToSys = '4'
    elif rateUser == '5️⃣':
        rateUserToSys = '5'


    macroCatChoice = macroCategNames[usersGlobalVariables[str(update.message.from_user.id)]["userChoiceMacroCategoryGlobal"]]

    numeroTurni = usersGlobalVariables[str(update.message.from_user.id)]["counterInteractionTurns"]

    constraintsUser = usersGlobalVariables[str(update.message.from_user.id)]["memoryConstraints"]

    #N.B. START BY 0 (index elements in menu per category)

    dishesLikedByUser = list(usersGlobalVariables[str(update.message.from_user.id)]["userRates"].items())

    urlDishesLiked = [ menu[int(item[0])].idDishUrl for item in dishesLikedByUser]

    starsTo5Random = [5] * usersGlobalVariables[str(update.message.from_user.id)]["numberLikes"]

    urlDishesShownToUser = ','.join(str(elem) for elem in usersGlobalVariables[str(update.message.from_user.id)]["listaDishesShown"])

    urlDishesPairwiseRecommendation = ','.join(str(elem[0])+" - "+str(elem[1]) for elem in usersGlobalVariables[str(update.message.from_user.id)]["listaDishesPairwiseRecommendation"])
    finalDishNotChosen = usersGlobalVariables[str(update.message.from_user.id)]["finalDishNotChosen"]

    #from datetime import date
    #codeMturk = str(update.message.from_user.id)+"-"+str(date.today().day)+""+str(date.today().month)+""+str(date.today().year)+"-"+tinyScenario+"-"+macroCatChoice.upper()

    codeMturk = get_random_string()

    usersGlobalVariables[str(update.message.from_user.id)]["mTurkCode"] = codeMturk

    nSkips = usersGlobalVariables[str(update.message.from_user.id)]["numberSkips"]
    nLikes = usersGlobalVariables[str(update.message.from_user.id)]["numberLikes"]

    #------------------------------------------------------------------------------------------------------------------
    # user_telegram_id;mturk_code;date;scenario;macro_categ;final_rate_service;duration_in_sec;pref_elic_duration_in_sec;recomm_duration_in_sec;number_interactions;has_user_perfermed_a_healthy_choice;nutri_score;fsa_score;id_dish_choice;user_constraints;proposal_random_1;proposal_random_2;proposal_random_3;proposal_random_4;proposal_random_5;number_skips;number_likes;all_dishes_shown_pref_elic;url_dishes_pairwise_comparisons;final_dish_not_chosen
    if nLikes == 5:
        lineaDaInserire = [update.message.from_user.id,codeMturk,dt_string,scenario,macroCatChoice,rateUserToSys,durataConversazione,durataInteraction,durataPresentation,numeroTurni,healthyChoice,healthinessPreferredDishNutri,healthinessPreferredDishFSA,idPreferredDish,','.join(str(elem) for elem in constraintsUser),urlDishesLiked[0],urlDishesLiked[1],urlDishesLiked[2],urlDishesLiked[3],urlDishesLiked[4], nSkips, nLikes, urlDishesShownToUser, urlDishesPairwiseRecommendation, finalDishNotChosen]
    elif nLikes == 4:
        lineaDaInserire = [update.message.from_user.id,codeMturk,dt_string,scenario,macroCatChoice,rateUserToSys,durataConversazione,durataInteraction,durataPresentation,numeroTurni,healthyChoice,healthinessPreferredDishNutri,healthinessPreferredDishFSA,idPreferredDish,','.join(str(elem) for elem in constraintsUser),urlDishesLiked[0],urlDishesLiked[1],urlDishesLiked[2],urlDishesLiked[3],"/", nSkips, nLikes, urlDishesShownToUser, urlDishesPairwiseRecommendation, finalDishNotChosen]
    elif nLikes == 3:
        lineaDaInserire = [update.message.from_user.id,codeMturk,dt_string,scenario,macroCatChoice,rateUserToSys,durataConversazione,durataInteraction,durataPresentation,numeroTurni,healthyChoice,healthinessPreferredDishNutri,healthinessPreferredDishFSA,idPreferredDish,','.join(str(elem) for elem in constraintsUser),urlDishesLiked[0],urlDishesLiked[1],urlDishesLiked[2],"/","/", nSkips, nLikes, urlDishesShownToUser, urlDishesPairwiseRecommendation, finalDishNotChosen]
    elif nLikes == 2:
        lineaDaInserire = [update.message.from_user.id,codeMturk,dt_string,scenario,macroCatChoice,rateUserToSys,durataConversazione,durataInteraction,durataPresentation,numeroTurni,healthyChoice,healthinessPreferredDishNutri,healthinessPreferredDishFSA,idPreferredDish,','.join(str(elem) for elem in constraintsUser),urlDishesLiked[0],urlDishesLiked[1],"/","/","/", nSkips, nLikes, urlDishesShownToUser, urlDishesPairwiseRecommendation, finalDishNotChosen]
    elif nLikes == 1:
        lineaDaInserire = [update.message.from_user.id,codeMturk,dt_string,scenario,macroCatChoice,rateUserToSys,durataConversazione,durataInteraction,durataPresentation,numeroTurni,healthyChoice,healthinessPreferredDishNutri,healthinessPreferredDishFSA,idPreferredDish,','.join(str(elem) for elem in constraintsUser),urlDishesLiked[0],"/","/","/","/", nSkips, nLikes, urlDishesShownToUser, urlDishesPairwiseRecommendation, finalDishNotChosen]


    import csv
    f = open("ratings.csv", "a")
    writer = csv.writer(f, delimiter=";")
    writer.writerow(lineaDaInserire)
    f.close()

    update.message.reply_text('Thanks for your rating!', reply_markup=ReplyKeyboardRemove())

    cancel(update, context)
    return 0


def main() -> None:
    """Run bot"""
    creaMenu()

    # Create the Updater and pass it the bot's token.
    updater = Updater("YOUR_TOKEN_:)")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states -> possibile reiterazione negli stati
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERCHOICEMODALITY: [MessageHandler(Filters.text, userChoiceModality)],
            FUNCTCALLBACK: [CallbackQueryHandler(zero, pattern='^'+str(0)+'$'),
                            CallbackQueryHandler(one, pattern='^'+str(1)+'$'),
                            CallbackQueryHandler(two, pattern='^'+str(2)+'$'),
                            CallbackQueryHandler(three, pattern='^' + str(3) + '$'),
                            CallbackQueryHandler(four, pattern='^' + str(4) + '$'),
                            CallbackQueryHandler(five, pattern='^' + str(5) + '$'),
                            CallbackQueryHandler(six, pattern='^' + str(6) + '$'),
                            CallbackQueryHandler(goToOtherConstraints, pattern='^'+str(7)+'$')],

            PROCESSUSERCONSTRAINTS: [MessageHandler(Filters.text, processUserConstraints)],

            FUNCTCALLBACK2: [CallbackQueryHandler(likeDishN, pattern='^' + "Like" + '$'),
                            CallbackQueryHandler(skipDishN, pattern='^' + "Skip" + '$')],

            FIRSTBRANCH: [MessageHandler(Filters.photo, firstBranch)],
            FIRSTBRANCH2: [MessageHandler(Filters.photo, firstBranch2), CommandHandler('skip', skipSendingImages)],
            PROCESSING: [MessageHandler(Filters.photo | Filters.text | Filters.command, processing), CommandHandler('skip', skipSendingImages)],
            AFTERRECOMMENDATION: [MessageHandler(Filters.text, afterRecommendation)],
            FINALRATINGS: [MessageHandler(Filters.text, finalRatings)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    #allow_reentry=True,
    dispatcher.add_handler(CommandHandler('cancel', cancel))
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling(timeout=15) #timeout=600

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
