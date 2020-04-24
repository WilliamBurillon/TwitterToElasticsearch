import tweepy
import requests
import json
from planar import BoundingBox
import time

#read config json file

with open("cfg.json") as json_data_file:
    cfg = json.load(json_data_file)

# Setup tweepy to authenticate with Twitter credentials:

auth = tweepy.OAuthHandler(cfg["twitter"]["CONSUMER_KEY"],cfg["twitter"]["CONSUMER_SECRET"])
auth.set_access_token(cfg["twitter"]["ACCESS_TOKEN"], cfg["twitter"]["ACCESS_SECRET"])

# Create the api to connect to twitter with your creadentials
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

headers = {
    'Content-Type': 'application/json',
}

def geoDataRefactor(dicGeo):
    """
    This function is a refactoring function. It goal is to replace the bounding box data into a single point
    :param dicGeo: Dictionnary which contains the place json from a tweet
    :return rDic: Dictionnary with coordinates instead of bounding box
    """
    rDic={}
    rDic["place_type"]=dicGeo["place_type"]
    rDic["name"]=dicGeo["name"]
    rDic["full_name"]=dicGeo["full_name"]
    rDic["country_code"]=dicGeo["country_code"]
    rDic["country"]=dicGeo["country"]
    bbox = BoundingBox(dicGeo["bounding_box"]["coordinates"][0])
    centerBbox=[bbox.center[0],bbox.center[1]]
    rDic["coordinates"]=centerBbox

    return rDic



def createDict(status):
    """
    This function creates a dictionnary with interesting data
    :param status: Represents the tweet
    :return toES: Represent the dict send to Elasticsearch
    """

    toES = {}
    toES["created_at"]=status._json["created_at"]
    toES["user_id"] = status._json["user"]["id_str"]
    toES["user_name"] = status._json["user"]["name"]
    source = status._json["source"]
    start = source.find("\">") + len("\">")
    end = source.find("</a>")
    reductedSource = source[start:end]
    toES["tweet_source"] = reductedSource
    try:
        toES["content"] = status._json["extended_tweet"]["full_text"]
    except:
        toES["content"]=status._json["text"]
    try:
        toES["hastag"] = status._json["extended_tweet"]["entities"]["hashtags"]
    except:
        toES["hastag"]=status._json["entities"]["hashtags"]
    toES["tweet_geo"]=geoDataRefactor(status._json["place"])
    return toES


class StreamListener(tweepy.StreamListener):
    """
    class to use the Streaming API
    """

    def on_status(self, status):

        if status._json["place"]!= None:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            print(current_time)
            toES = createDict(status)
            response = requests.post("https://elastic:"+cfg["elasticsearch"]["password"]+"@"+cfg["elasticsearch"]["endpoint"]+"/tweet/_doc",headers=headers, data=json.dumps(toES))
            print(response)

    def on_error(self, status_code):
        if status_code == 420:
            return False


if __name__=="__main__":
    stream_listener = StreamListener()
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=["coronavirus","COVID-19"])
