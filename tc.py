#!/usr/bin/env python3
from twitter import *
from tokens import *

user = "YSLPlug"

"""
Erkenntnisse:
 - Timeline-Requests sind limitiert auf 900 pro 15-Minuten Window
 - Aus einer Timeline können maximal die letzten 3200 Tweets gelesen werden (Tweets inkl. Retweets)
 - Pro Request können maximal 200 Tweets gelesen werden (=Page)
 - Werden Retweets nicht angefordert, fehlen sie in der Antwort (die Page wird kleiner)
 - Die Timeline wird per Paging gecrawled, das letzte Element ist auch in der nächsten Page wieder drin
 - Maximale Tweets pro 15 Minuten: 900 Requests * 200 Tweets / Page = 180.000 Tweets pro 15 Minuten
 - in 24h 2.6 mio Tweets maximum (unter optimalen Bedingungen)
"""


def print_error(twitter_http_error):
    error = twitter_http_error.response_data["errors"][0]
    message, code = error["message"], error["code"]
    print("Twitter-Fehler: {0} (Code {1})".format(message, code))


def read_page(max_id=None, include_rts=False):
    if not max_id:
        tweets = [Tweet(raw) for raw in t.statuses.user_timeline(
            screen_name=user,
            count=200,
            include_rts=include_rts)]
    else:
        # this is a page, filter out the first element as it is also the last
        # element of the previous page
        response = t.statuses.user_timeline(
            screen_name=user,
            count=200,
            include_rts=include_rts,
            max_id=max_id)

        tweets = [Tweet(raw) for raw in response]

    max_id = tweets[-1].id

    return (max_id, tweets)


def read_full_timeline(include_rts=False):
    last_max_id, tweets = read_page(include_rts=include_rts)

    while True:
        next_max_id, more_tweets = read_page(
            last_max_id, include_rts=include_rts)

        if next_max_id == last_max_id:
            # is there a better way to do this? last_page_indicator or something like that?
            break

        tweets += more_tweets
        last_max_id = next_max_id

    return tweets


class Tweet(object):

    def __init__(self, raw):
        self.raw = raw
        self.text = raw["text"]
        self.lang = raw["lang"]
        self.id = raw["id"]
        self.geo = raw["geo"]

    def __str__(self):
        return "{0} (id={1}, lang={2})".format(self.text, self.id, self.lang)


if __name__ == "__main__":

    t = Twitter(auth=OAuth(TOKEN,
                           TOKEN_SECRET,
                           CONSUMER_KEY,
                           CONSUMER_SECRET))

    tweets = read_full_timeline(include_rts=False)

    for tweet in tweets:
        print(tweet)

    print("Done. {0} tweets".format(len(tweets)))
