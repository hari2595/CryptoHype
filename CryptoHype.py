# Packages needed

import praw
import tweepy
from datetime import datetime
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests
import RedditLists
import Keys
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
########################################################################################################################

# root used for google search

root = "https://www.google.com/"
link = f"https://www.google.com/search?q={str(RedditLists.us)}&tbm=nws&source=lnt&tbs=qdr:d&sa=X&ved=2ahUKEwjK0uL5-p31AhWejYkEHZcCADQQpwV6BAgBEBY&biw=1536&bih=722&dpr=1.25"


########################################################################################################################

def data_extractor(reddit):

    # set the program parameters

    subs = ['CryptoCurrency']  # sub-reddit to search
    uniqueCmt = True  # allow one comment per author per symbol
    upvoteRatio = 0.70  # upvote ratio for post to be considered, 0.70 = 70%
    ups = 20  # define # of upvotes, post is considered if upvotes exceed this #
    limit = 1  # define the limit, comments 'replace more' limit
    upvotes = 1  # define # of upvotes, comment is considered if upvotes exceed this #
    picks = 10  # define # of picks here, prints as "Top ## picks are:"
    picks_ayz = 5  # define # of picks for sentiment analysis

    posts, count, c_analyzed, tickers, titles, a_comments = 0, 0, 0, {}, [], {}
    cmt_auth = {}

    for sub in subs:
        subreddit = reddit.subreddit(sub)
        hot = subreddit.hot()  # sorting posts by hot
        # Extracting comments, symbols from subreddit
        for submission in hot:


            # checking: post upvote ratio # of upvotes, post flair, and author
            if submission.upvote_ratio >= upvoteRatio and submission.ups > ups:
                submission.comment_sort = 'new'
                comments = submission.comments
                titles.append(submission.title)
                posts += 1
                try:
                    submission.comments.replace_more(limit=limit)
                    for comment in comments:
                        # try except for deleted account?
                        try:
                            auth = comment.author.name
                        except:
                            pass
                        c_analyzed += 1

                        # checking: comment upvotes and author
                        if comment.score > upvotes:
                            split = comment.body.split(" ")
                            for word in split:
                                word = word.replace("$", "")

                                if word in RedditLists.us:

                                    # unique comments, try/except for key errors
                                    if uniqueCmt:
                                        try:
                                            if auth in cmt_auth[word]: break
                                        except:
                                            pass

                                    # counting tickers
                                    if word in tickers:
                                        tickers[word] += 1
                                        a_comments[word].append(comment.body)
                                        cmt_auth[word].append(auth)
                                        comments_df = pd.DataFrame(a_comments[word], columns=['comment'])
                                        filename = 'scraped_comments.csv'

                                        # we will save our database as a CSV file.
                                        comments_df.to_csv(filename, mode='a')

                                        count += 1

                                    else:
                                        tickers[word] = 1
                                        cmt_auth[word] = [auth]
                                        a_comments[word] = [comment.body]
                                        comments_df = pd.DataFrame(a_comments[word], columns=['comment'])
                                        filename = 'scraped_comments.csv'

                                        # we will save our database as a CSV file.
                                        comments_df.to_csv(filename, mode='a')


                                        count += 1
                except Exception as e:
                    print(e)

    return posts, c_analyzed, tickers, titles, a_comments, picks, subs, picks_ayz


def main():
    # reddit client
    reddit = praw.Reddit(user_agent=Keys.ua,
                         client_id=Keys.reddit_id,
                         client_secret=Keys.reddit_client_secret,
                         username=Keys.user,
                         password=Keys.pwd)

    data_extractor(reddit)

#######################################################################################################################


# function to perform data extraction
def scrape(words, date_since, numtweet):

    auth = tweepy.OAuthHandler(Keys.consumer_key, Keys.consumer_secret)
    auth.set_access_token(Keys.access_token, Keys.access_token_secret)
    api = tweepy.API(auth)

    # Creating DataFrame using pandas
    db = pd.DataFrame(columns=['username', 'description', 'location', 'following',
                               'followers', 'totaltweets', 'retweetcount', 'text', 'hashtags'])

    # We are using .Cursor() to search through twitter for the required tweets.
    # The number of tweets can be restricted using .items(number of tweets)
    tweets = tweepy.Cursor(api.search_tweets, q=words, lang="en",
                           since=date_since, tweet_mode='extended').items(numtweet)

    # .Cursor() returns an iterable object. Each item in
    # the iterator has various attributes that you can access to
    # get information about each tweet
    list_tweets = [tweet for tweet in tweets]

    # Counter to maintain Tweet Count
    i = 1

    # we will iterate over each tweet in the list for extracting information about each tweet
    for tweet in list_tweets:
        username = tweet.user.screen_name
        description = tweet.user.description
        location = tweet.user.location
        following = tweet.user.friends_count
        followers = tweet.user.followers_count
        totaltweets = tweet.user.statuses_count
        retweetcount = tweet.retweet_count
        hashtags = tweet.entities['hashtags']

        # Retweets can be distinguished by a retweeted_status attribute,
        # in case it is an invalid reference, except block will be executed
        try:
            text = tweet.retweeted_status.full_text
        except AttributeError:
            text = tweet.full_text
        hashtext = list()
        for j in range(0, len(hashtags)):
            hashtext.append(hashtags[j]['text'])

        # Here we are appending all the extracted information in the DataFrame
        ith_tweet = [username, description, location, following,
                     followers, totaltweets, retweetcount, text, hashtext]
        db.loc[len(db)] = ith_tweet


    filename = 'scraped_tweets.csv'

    # we will save our database as a CSV file.
    db.to_csv(filename)


def TweetData():
    # Read Hashtag and date
    words = RedditLists.us
    date_since = datetime.today().strftime('%Y-%m-%d')

    # number of tweets you want to extract in one run
    numtweet = 500
    scrape(words, date_since, numtweet)

########################################################################################################################

# Function to search google news results from past 24 hrs
def news(link):
    req = Request(link, headers={'User-Agent': 'Chrome/97.0.4692.71'})
    webpage = urlopen(req).read()
    with requests.Session() as c:
        try:

            soup = BeautifulSoup(webpage, 'html5lib')

            for item in soup.find_all('div', attrs={'class': 'ZINbbc xpd O9g5cc uUPGi'}):

                desc = (item.find('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})).get_text()

                desc = desc.split(' � ')[1]
                desc = desc.replace(","," ")

                df = pd.DataFrame([x.split(';') for x in desc.split('\n')[1:]], columns=[x for x in desc.split('\n')[0].split(';')])
                filename = 'scraped_news.csv'

                # we will save our database as a CSV file.s
                df.to_csv(filename, mode='a')
                
            next = soup.find('a', attrs={'aria-label': 'Next page'})
            link = (next['href'])
            link = root+link
            news(link)

        except:
            pass


########################################################################################################################

# function to analyze the sentiment score with Vader
def score():
    # Importing csv files from the previous functions and cleaning the data
    df1 = pd.read_csv('scraped_news.csv', encoding='cp850', header=None, sep='\n')
    df1 = df1[0].str.split('\s\|\s', expand=True)
    df2 = pd.read_csv("scraped_comments.csv", encoding='cp850')
    df2.drop(index=df2[df2['comment'] == 'comment'].index, inplace=True)
    df2 = df2['comment']
    df3 = pd.read_csv("scraped_tweets.csv", encoding='cp850')
    df3 = df3['text']
    
    frame = [df1, df2, df3]
    df = pd.concat(frame)
    df.reset_index(drop=True, inplace=True)

    # Assigining the vader inbuilt analyzer
    analyzer = SentimentIntensityAnalyzer()
    
    # Adding reddit and twitter lingo to the lexicon
    analyzer.lexicon.update(RedditLists.new_words)
    
    # Setting counters to add the positive / negative sentiment count of each line. The programs goes through each of the lines in the dataframe as seen in the for loop below
    pos = 0
    PosCount = 0

    neg = 0
    NegCount = 0

    for i in range(df.shape[0]):
        text = df.iloc[i, 0]
        text_analyzer = analyzer.polarity_scores(text)
        if text_analyzer['compound'] > 0:
            pos += 1
        PosCount += 1

        if text_analyzer['compound'] <= 0:
            neg += 1
        NegCount += 1
    
    # Computing the scores
    
    positive_score = pos / PosCount * 100.0
    negative_score = neg / NegCount * 100.0
    print("The positive sentiment is" )
    print(positive_score)
    print("The negative sentiment is")
    print(negative_score)

########################################################################################################################

# Token name that is going to be searched

def input_token():
    print("Enter Token name")
    RedditLists.us = input()


if __name__ == '__main__':
    input_token()
    main()
    TweetData()
    news(link)
    score()
