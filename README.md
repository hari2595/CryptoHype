## CryptoHype
### A simple social media sentiment analysis done for crypto currencies. 

### Scours through the internet to find the current pubic sentiment.
Uses twitter API, reddit API

## Libraries used:
- praw,
- tweepy,
- datetime,
- urllib.request - Request, urlopen,
- bs4 - BeautifulSoup,
- requests,
- RedditLists,
- Keys,
- vaderSentiment.vaderSentiment - SentimentIntensityAnalyzer,
- pandas,

## Input:
- Crypto token full name.

## Searches in:
- Subreddits from Reddit .com (customizable list),
- Twitter tweets,
- Google News,

## Output:
- Shows the positive and negative sentiment of crypto coin searched in scale of 0.00 -1.00

## Comment:
Since exception in output, do not worry about it. Tweepy updated their library and removed the since function but the program still works without a problem.
