# TwitterToElasticsearch

This project contains a Python script which allow ot get tweets from Twitter API and inject them to Elasticsearch 

To use this script, make sure you have created a JSON config file cfg.json like that :

## cfg.json
'''json
{
  "twitter" : {
    "ACCESS_TOKEN" : "XXX",
    "ACCESS_SECRET" : "XXX",
    "CONSUMER_KEY" : "XXX",
    "CONSUMER_SECRET" : "XXX"

  },
  "elasticsearch": {
      "password" : "XXX",
      "endpoint" : "XXXXXX"
  }
}
'''
