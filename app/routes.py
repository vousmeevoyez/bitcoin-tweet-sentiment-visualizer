from app import app
from flask import render_template,request,jsonify
from flask_pymongo import PyMongo
from bson import ObjectId

mongo = PyMongo(app)

@app.route('/')
def index_page():
    output = []
    result = mongo.db.train_sample.aggregate([{"$sample":{"size":10 }}])

    for item in result:
        tweet = {
            "raw_tweet": item["tweet"],
            "sentiment" : item["sentiment"]["label"],
            "raw_token" : item["stop_words_token"],
            "token"     : item["token"]
        }
        output.append(tweet)

    title = "Bitcoin Sentiment Analysis with VADER & Fuzzy String Matching using Twitter Data "
    date = ["2017-12-26","2017-12-27","2017-12-28","2017-12-29","2017-12-30","2017-12-31","2018-01-01"]
    return render_template("sentiment.html", title=title , tweets=output , date=date)

@app.route('/api_get_sentiment_analysis_daily_url',methods=['GET','POST'])
def sentiment_daily_result():
    data = request.form.to_dict()
    sample_date = data["sample_date"]

    result = mongo.db.sentiment_analysis.find_one({
        "sample_date" : sample_date
    })

    result["_id"] = ""
        
    return jsonify({ "result" : result })

@app.route('/api_get_sentiment_analysis_summary_url',methods=['GET'])
def sentiment_summary_result():

    result = mongo.db.sentiment_analysis.find_one({
        "_id" : ObjectId("5a4991f3a081af5a3f529b33")
    })

    result["_id"] = ""        
    return jsonify({ "result" : result })
