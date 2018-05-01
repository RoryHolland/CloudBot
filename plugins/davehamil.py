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

    phrase = text_model.make_sentence().replace(" '", "'").replace(" .", ".").replace(" !", "!").replace(" ?", "?").replace(" ,", ",")
    if len(phrase) < 60:
        phrase = phrase + " " + text_model.make_sentence().replace(" '", "'").replace(" .", ".").replace(" !", "!").replace(" ?", "?").replace(" ,", ",")
    
    # act out the message
    message(phrase)

