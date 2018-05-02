import codecs
import json
import os
import random
import asyncio
import re
import markovify
import spacy
from random import randint

from cloudbot import hook
from cloudbot.util import textgen

nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[\{\}\*]*$", re.I)

import en_core_web_sm
nlp = en_core_web_sm.load()

class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        return ["::".join((word.orth_, word.pos_)) for word in nlp(sentence)]

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

@hook.on_start()
def load_text(bot):
    """
    :type bot: cloudbot.bot.CloudBot
    """
    global text_model

    with codecs.open(os.path.join(bot.data_dir, "dh"), encoding="utf-8") as f:
        # Get raw text as string.
        text = f.read()
    # Build the model.
    text_model = POSifiedText(text)

@asyncio.coroutine
@hook.command
def dh(text, message):

    phrase = process_phrase(text_model.make_short_sentence(61)).capitalize()
    while len(phrase) < 60:
        phrase = "{}. {}".format(phrase, process_phrase(text_model.make_sentence()).capitalize())
    
    # act out the message
    message(process_phrase(phrase))


def process_phrase(phrase):
    # Remove spaces before apostrophes
    phrase = phrase.replace(" '", "'")

    # Remove spaces before full-stops
    phrase = phrase.replace(" .", ".")

    # Remove spaces before exclamation marks
    phrase = phrase.replace(" !", "!")

    # Remove spaces before question marks
    phrase = phrase.replace(" ?", "?")

    # Remove spaces before commas
    phrase = phrase.replace(" ,", ",")

    # Remove spaces which appear in words like can't and don't
    phrase = phrase.replace(" n't", "n't")

    # Hack to preserve elipses when running process_phrase() multiple times
    phrase = phrase.replace("...", ".....")

    # Remove duplicate full-stops
    phrase = phrase.replace("..", ".")

    # Remove full-stop after question mark
    phrase = phrase.replace("?.", "?")

    # Remove full-stop after exclamation mark
    phrase = phrase.replace("!.", "!")

    # Remove duplicate whitespace
    phrase = ' '.join(phrase.split())
    return phrase
