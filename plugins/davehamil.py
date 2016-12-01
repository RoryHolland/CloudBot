import codecs
import json
import os
import random
import asyncio
import re
import markovify
from random import randint

from cloudbot import hook
from cloudbot.util import textgen

nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[\{\}\*]*$", re.I)

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
    text_model = markovify.Text(text)

@asyncio.coroutine
@hook.command
def dh(text, message):

    phrase = text_model.make_short_sentence(randint(30,300))
    # act out the message
    message(phrase)

