import re
import random

from sqlalchemy import Table, Column, String, PrimaryKeyConstraint

from cloudbot.event import EventType
from cloudbot import hook
from cloudbot.util import database

table = Table(
    'badwords',
    database.metadata,
    Column('word', String),
    Column('nick', String),
    Column('chan', String),
    PrimaryKeyConstraint('word', 'chan')
)


@hook.on_start()
@hook.command("loadbad", permissions=["badwords"], autohelp=False)
def load_bad(db):
    """- Should run on start of bot to load the existing words into the regex"""
    global badword_re, blacklist, black_re
    words = db.execute("select word from badwords").fetchall()
    out = ""
    for word in words:
        out = out + "{}|".format(word[0])
    blacklist = out[:-1]
    black_re = '(\s|^|[^\w\s])({0})(\s|$|[^\w\s])'.format(blacklist)
    badwords_re = re.compile(black_re, re.IGNORECASE)


@hook.command("addbad", permissions=["badwords"])
def add_bad(text, nick, db, conn):
    """<word> <channel> - adds a bad word to the auto kick list must specify a channel with each word"""
    global blacklist, black_re, blacklist
    word = text.split(' ')[0].lower()
    channel = text.split(' ')[1].lower()
    if not channel.startswith('#'):
        return "Please specify a valid channel name after the bad word."
    word = re.escape(word)
    wordlist = list_bad(channel, db, conn)
    if word in wordlist:
        return "{} is already added to the bad word list for {}".format(
            word,
            channel)
    else:
        if len(
            db.execute(
                "select word from badwords where chan = :chan", {
                "chan": channel}).fetchall()) < 10:
            db.execute(
                "insert into badwords ( word, nick, chan ) values ( :word, :nick, :chan)", {
                    "word": word, "nick": nick, "chan": channel})
            db.commit()
            load_bad(db, conn)
            wordlist = list_bad(channel, db, conn)
            return "Current badwords: {}".format(wordlist)
        else:
            return "There are too many words listed for channel {}. Please remove a word using .rmbad before adding anymore. For a list of bad words use .listbad".format(
                channel)


@hook.command("rmbad", "delbad", permissions=["badwords"])
def del_bad(text, db, conn):
    """<word> <channel> - removes the specified word from the specified channels bad word list"""
    global blacklist, black_re, blacklist
    word = text.split(' ')[0].lower()
    if not (text.split(' ')[1] or text.split(' ')[1]('#')):
        return "please specify a valid channel name"
    channel = text.split(' ')[1].lower()
    db.execute(
        "delete from badwords where word = :word and chan = :chan", {
            "word": word, "chan": channel})
    db.commit()
    newlist = list_bad(channel, db, conn)
    load_bad(db, conn)
    return "Removing {} new bad word list for {} is: {}".format(
        word,
        channel,
        newlist)


@hook.command("listbad", permissions=["badwords"])
def list_bad(text, db):
    """<channel> - Returns a list of bad words specify a channel to see words for a particular channel"""
    text = text.split(' ')[0].lower()
    out = ""
    if not text.startswith('#'):
        return "Please specify a valid channel name"
    words = db.execute(
        "select word from badwords where chan = :chan", {
            "chan": text}).fetchall()
    for word in words:
        out = out + "{}|".format(word[0])
    return out[:-1]


@hook.event([EventType.message, EventType.action], singlethread=True)
def test_badwords(event, db, conn, message):
    match = re.search(black_re, event.content, re.IGNORECASE)
    if match:
        # Check to see if the match is for this channel
        word = match.group().lower().strip()
        check = db.execute(
            "select word, nick from badwords where word = :word and chan = :chan", {
                "word": word, "chan": event.chan}).fetchone()
        if (check) or ((word == "fap") and (event.chan == "#conversations")):
            out = "KICK {} {} :that fucking word is so damn offensive".format(
                event.chan,
                event.nick)
            message(
                "{}, congratulations you've won!".format(
                    event.nick),
                event.chan)
            conn.send(out)
        else:
            pass
