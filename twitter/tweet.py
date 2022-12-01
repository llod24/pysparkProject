import tweepy
import json
import pyspark


bearer_token = "AAAAAAAAAAAAAAAAAAAAAL60jgEAAAAAM%2FlGZy2vYiMx6UqhD73jMnzZwl0%3DIpkhxidEWvwV0daNGljKXsy4l2heR8hIJBfdskbETfwVQNH0nH"
contry_word = {
            'Australia': ['australia'],
            'Japan': ['japan'],
            'Iran': ['iran'],
            'Qatar': ['qatar'],
            'SaudiArabia': ['saudi arabia', 'saudiarabia'],
            'SouthKorea': ['korea', 'south korea', 'southkorea'],
            'Cameroon': ['carmeroon'],
            'Ghana': ['ghana'],
            'Morocco': ['morocco'],
            'Senegal': ['senegal'],
            'Tunisia': ['tunisia'],
            'Canada': ['canada'],
            'CostaRica': ['costarica', 'costa rica'],
            'Mexico': ['mexico'],
            'UnitedStates': ['unitedstates', 'united states', 'ameria'],
            'Argentina': ['argentina'],
            'Brazil': ['brazil'],
            'Ecuador': ['ecuador'],
            'Uruguay': ['uruguay'],
            'Belgium': ['belgium'],
            'Croatia': ['coratia'],
            'Denmark': ['denmark'],
            'England': ['england'],
            'France': ['france'],
            'Germany': ['germany'],
            'Netherlands': ['netherlands'],
            'Poland': ['poland'],
            'Portugal': ['portugal'],
            'Serbia': ['serbia'],
            'Spain': ['spain'],
            'Switzerland': ['switzerland'],
            'Wales': ['wales']}

def remove_sign(x):
    signs = ['`', '!', '@', '#', '$', '%', '^', '&', '*',
            '(', ')', '_', '-', '+', '=', '[', ']', '{', '}',
            ';', ':', '\"', '\'', '\\', '.', ',', '?', '/',
            '<', '>', '~', '|', '\n']
    result = x
    for sign in signs:
        result = result.replace(sign, " ")
    return result

def map_contry(x):
    result = {}
    for c in contry_word.keys():
        result[c] = 0
        for word in contry_word[c]:
            if word in x:
                result[c] += 1
                break
    return result
    

class Tweet:
    def __init__(self) -> None:
        
        self.tweet_dic = {}
        self.bearer_token = "AAAAAAAAAAAAAAAAAAAAAL60jgEAAAAAM%2FlGZy2vYiMx6UqhD73jMnzZwl0%3DIpkhxidEWvwV0daNGljKXsy4l2heR8hIJBfdskbETfwVQNH0nH"
        self.client = tweepy.Client(bearer_token)
        self.myConf = pyspark.SparkConf()
        self.spark = pyspark.sql.SparkSession.builder.getOrCreate()
        self.collect_result = None
        
    def read_from_tweet(self, tag_list, limit):
        for hashtag in tag_list:
            # Get tweets that contain the hashtag #petday
            # -is:retweet means I don't wantretweets
            # lang:en is asking for the tweets to be in english
            query = f'#{hashtag} -is:retweet lang:en'
            tweets = tweepy.Paginator(self.client.search_recent_tweets, 
                                      query=query,
                                      tweet_fields=['context_annotations', 'created_at'], 
                                      max_results=100).flatten(limit=limit)

            for tweet in tweets:
                if tweet.id in self.tweet_dic:
                    continue
                else:
                    self.tweet_dic[tweet.id] = tweet.text

    
    
    def count_by_spark(self):
        textRDD = self.spark.sparkContext.parallelize(self.tweet_dic.values())
        wordRDD = textRDD.map(remove_sign)
        wordRDD = wordRDD.map(lambda x:x.lower())
        wordRDD = wordRDD.map(map_contry)
        wordRDD = wordRDD.flatMap(lambda x:x.items())
        wordRDD = wordRDD.reduceByKey(lambda x, y: x + y)
        wordRDD = wordRDD.sortBy(lambda x: -x[1])
        self.collect_result = wordRDD.collect()
    
    def convert_write_json(self):
        if self.collect_result is None:
            return False
        d = {}
        for k, v in self.collect_result:
            d[k] = v
        return json.dumps(d)
        # jf = json.dumps(d)
        #with open('collect_result.json', 'w') as f:
            #json.dump(d,f)
    
    def do(self, tag_list, limit):
        self.read_from_tweet(tag_list, limit)
        self.count_by_spark()
        return self.convert_write_json()



