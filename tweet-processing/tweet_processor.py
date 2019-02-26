import argparse
import json
import time
import string
import pymongo
import preprocessor as p 
from datetime      import datetime,timedelta
from nltk.tokenize import TweetTokenizer
from nltk          import bigrams
from nltk.corpus   import stopwords
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fuzzywuzzy    import process
from fuzzywuzzy    import fuzz
from collections   import Counter

start_time = time.time()

"""
    Tweet Preprocessor Script

    Script to load tweet data from JSON or CSV, extract the tweet data and analyze it

    Code written by Kelvin
"""

class TweetProcessor(object):

    source = ""
    output = ""

    # tweet statistic
    tweet_statistic = {
        "load_counter"   : 0,
        "defect_counter" : 0
    }

    #sentiment statistic
    sentiment_statistic = {
        "positive" : 0,
        "neutral"  : 0,
        "negative" : 0
    }

    #initialize stop word 
    punctuation = list(string.punctuation)
    tweet_term = ['rt' , 'via' , '...'] 
    stop = stopwords.words('english') + punctuation + tweet_term

    #initialize counter list
    count_all = Counter()
    hashtag_all = Counter()
    single_all = Counter()

    # seen
    seen = []

    def __init__(self,source,output):
        self.source = source
        self.output = output

    def generate_token_sanitize(self,tweet):
        """
            Break tweet smaller into token-token 
            and remove stop words
            Arguments : 
                tweet -- string 
            Return :
                Token -- list
        """
        tweet = tweet.lower()
        tweet_tokenizer = TweetTokenizer()
        token = tweet_tokenizer.tokenize(tweet)
        clean_tweet = [term for term in token if term not in self.stop]
        return ' '.join(clean_tweet)

    def generate_token(self,tweet):
        """
            Break tweet smaller into token
            Arguments:
                tweet -- string
            return:
                token -- list
        """
        tweet = tweet.lower()
        tweet_tokenizer = TweetTokenizer()
        token = tweet_tokenizer.tokenize(tweet)
        return token

    def check_sentiment(self,tweet):
        """
            determine tweet whether it is positive, netral or negative
            0 <= x <= 1
            Arguments :
                tweet -- List
            Return :
                result -- dictionary (label,polarity)
        """
        result = {
            "label"    : "",
            "polarity" : ""
        }
        analyzer = SentimentIntensityAnalyzer()
        analysis_result = analyzer.polarity_scores(tweet)
        polarity = analysis_result['compound']

        if polarity > 0 :
            label = 'positive'
        elif polarity == 0:
            label = 'neutral'
        else:
            label = 'negative'

        result['polarity'] = polarity
        result['label']    = label
        return result

    def check_fuzzy(self,tweet):
        """
            Fuzzy String matching
            Arguments : 
                tweet -- string
            Return : 
                closeness -- int
        """
        fuzzy_result = process.extractOne(tweet,self.seen,scorer=fuzz.token_set_ratio)
        return fuzzy_result

    def json_processing(self,start,batch_size):
        """
            load tweet from json file
            Arguments :
                filename   -- filepath string
                batch_size -- limit how many tweet that we want to be loaded
            return :
                Tweets - List
        """

        counter        = 0
        defect_counter = 0

        filename = self.source
        with open(filename,'r') as f:
            for i,line in enumerate(f):
                if i >= start:
                    try:
                        tweet_details = json.loads(line)
                        if counter == batch_size:
                            break
                        try:
                            tweet = tweet_details['text']
                            tweet = tweet.encode('utf-8')
                            tweet = unicode(tweet,errors='ignore')

                            created_at  = tweet_details["created_at"]
                            created_at  = datetime.strptime(created_at, "%a %b %d %H:%M:%S +0000 %Y")

                            token_tweet = self.generate_token(tweet)
                            stop_words_token = self.generate_token_sanitize(tweet)

                            tweet_load = {
                                "tweet"            : tweet,
                                "token"            : token_tweet,
                                "stop_words_token" : stop_words_token,
                            }

                            if len(self.seen) != 0:
                                fuzzy_result = self.check_fuzzy(tweet)
                                if fuzzy_result[1] < 50:
                                    analyze_result = self.analyze_tweet(tweet)
                                    print "--------TWEET---------"
                                    print fuzzy_result
                                    print created_at
                                    print json.dumps(tweet_load)
                                    print analyze_result
                                self.seen.append(tweet)
                            else:
                                print "once"
                                self.seen.append(tweet)

                            counter +=1
                            print counter
                        except Exception, e:
                            print str(e)
                            next(f)
                            defect_counter += 1
                    except Exception,e:
                            print str(e)
                            next(f)
                            defect_counter += 1

        current_counter = self.tweet_statistic['load_counter'] 
        current_defect  = self.tweet_statistic["defect_counter"]
        self.tweet_statistic['load_counter'  ] = current_counter + counter 
        self.tweet_statistic['defect_counter'] = current_defect  + defect_counter

    def load_tweet_csv(self):
        """
            load tweet from csv file
            Arguments :
                filename -- filepath string
            return :
                Tweets - List
        """
        counter = 0
        defect_counter = 0

        csv = self.source
        with open(csv,"r") as f:
            for line in f :
                try:
                    data = line.split(',')
                    label = data[0]
                    tweet = data[1]
                    tweet_load = {
                            "tweet" : tweet,
                    }
                    print "---tweet-----"
                    print tweet
                    counter +=1
                except Exception,e:
                    print "error " + str(e)
                    next(f)
                    defect_counter += 1

        tweet_statistic['load_counter'] = counter
        tweet_statistic['defect_counter'] = defect_counter
        return tweets

    def analyze_tweet(self,tweet):

        """
            analyze tweet and return statistical data like word frequency, polarity,etc..
            Arguments:
                Tweets - filtered tweet

            Return:
                result - tweet analysis result
        """

        # sentiment_counter
        positive = 0
        neutral  = 0
        negative = 0

        #terms all
        terms_all = [term for term in self.generate_token(tweet)]
        # terms single
        terms_single = set(terms_all)
        # terms hashtag only
        terms_hash   = [term for term in self.generate_token(tweet) if term.startswith('#')]
        # terms only
        terms_only = [term for term in self.generate_token(tweet) if term not in self.stop and not term.startswith(('#', '@'))]
        # removing stop word
        clean_tweet = self.generate_token_sanitize(tweet)

        #sentiment analysis using textblob
        sentiment_result   = self.check_sentiment(clean_tweet)
        sentiment_label    = sentiment_result['label']
        sentiment_polarity = sentiment_result['polarity']

        print "%s( %.2f ) - %s" % (sentiment_label,sentiment_polarity,clean_tweet)
        analyze_result = {
            "tweet"    : clean_tweet,
            "polarity" : sentiment_polarity,
            "label"    : sentiment_label
        }

        #count tweet sentiment
        if sentiment_label == 'positive' : 
            positive +=1
        elif sentiment_label == 'neutral':
            neutral += 1
        else:
            negative +=1

        #update terms
        self.single_all.update(terms_single)
        self.count_all.update(terms_only)
        self.hashtag_all.update(terms_hash)

        current_positive = self.sentiment_statistic['positive'] 
        current_neutral  = self.sentiment_statistic['neutral'] 
        current_negative = self.sentiment_statistic['negative']

        self.sentiment_statistic['positive'] = current_positive + positive
        self.sentiment_statistic['neutral']  = current_neutral  + neutral
        self.sentiment_statistic['negative'] = current_negative + negative

        return analyze_result

    def write_to_csv(self,tweet):
        """
            Write CSV file 
        """
        csv_output = self.output
        tweet_seen = set()
        outfile = open(csv_output,"a")

        tweet = tweet['tweet']
        p.set_options(p.OPT.URL ,p.OPT.EMOJI)
        clean_tweet = p.clean(tweet)
        sentiment_label    = sentiment_result['label']
        if tweet not in tweet_seen:
            row = sentiment_label + ',' + clean_tweet + '\n'
            print row
            outfile.write(row)
            tweet_seen.add(tweet)
        outfile.close()

    def connect_db():
        """
            Connect to database
        """
        try:
            conn = pymongo.MongoClient()
            print "Connection initialized"
            db   = conn.tweetDB
            collection = db.tweet_train_dataset
        except pymongo.errors.ConnectionFailure,e:
            print "Error connecting %s" % e

    def display_stats(self):
        tweet_statistic = self.tweet_statistic
        sentiment_statistic = self.sentiment_statistic
        output = {
            "tweet_statistic" : tweet_statistic,
            "sentiment_statistic" : sentiment_statistic
        }
        with open(self.output,"a") as outfile:
            json.dump(output,outfile)

#end class

data_amount = 1000000
batch_group = 10

# filename ( raw tweet , filtered tweet and tweet summary)
filename = "tweet_data/stream_bitcoin.json"
output1  = "tweet_summary.json"
csv_output = "tweet_label_full_dataset.csv"

test = TweetProcessor(filename,"test.json")
test.json_processing(1,100000)
test.display_stats()
