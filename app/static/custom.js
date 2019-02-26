var bitcoin_array = []
var output_chart = ['2017-12-26','2017-12-27','2017-12-28', '2017-12-29','2017-12-30','2017-12-31','2018-01-01']

$(document).ready(function(){
	get_bitcoin_price();
	get_sentiment_summary();
	for (i=0; i < output_chart.length; i++){
		date = output_chart[i];
		get_sentiment_stats(date);
	}
});

get_bitcoin_price = function()
{
	AJAX_SERVER(
		get_bitcoin_price_CALLBACK,
		"POST",
		"/api_get_bitcoin_price_url",
		{
			"page_num" : 1,
			"page_size" : 2000,
		},
		true
	);
}

get_bitcoin_price_CALLBACK = function(msg_json)
{	
	inner_price_array = []
	inner_time_array  = []

	inner_price_array.push('Bitcoin Price');
	inner_time_array.push('x');

	console.log(msg_json);
	result = msg_json.result;
	result.forEach(function(item){
		price_at = new Date(item.price_at);
		price    = item.price;
		inner_time_array.push(price_at);
		inner_price_array.push(parseInt(price));
	});
	bitcoin_array.push(inner_time_array);
	bitcoin_array.push(inner_price_array);
	console.log(bitcoin_array);

	//Generate chart using c3js
	var chart = c3.generate({
		bindto : '#chart',
		data : {
			x : 'x',
			columns: bitcoin_array
		},
		axis: {
			x : {
				type : 'timeseries',
				tick : {
					values : [],
					format : '%Y-%m-%d %H:%M:%S'
				} 
			}
		}
	});	
}

get_sentiment_stats = function(sample_date)
{
	AJAX_SERVER(
		get_sentiment_stats_CALLBACK,
		"POST",
		"api_get_sentiment_analysis_daily_url",
		{
			sample_date : sample_date
		},
		true
	)
}

get_sentiment_stats_CALLBACK = function(msg_json)
{
	var most_common_tweet_arr  = [];
	var most_hashtag_tweet_arr = [];

	var inner_column1_arr = [];
	var inner_label1_arr = [];

	var inner_column2_arr = [];
	var inner_label2_arr = [];

	/*
	 *		MOST COMMON TWEET
	 * */
	inner_column1_arr.push('data1');
	inner_label1_arr.push('x');

	console.log(msg_json);
	result = msg_json.result;

	most_common_tweet = result.most_common_tweet;
	for (i = 0; i <= 10; i++){
		label = most_common_tweet[i][0];
		value = most_common_tweet[i][1];
		inner_column1_arr.push(value);
		inner_label1_arr.push(label);
	};

	most_common_tweet_arr.push(inner_label1_arr);
	most_common_tweet_arr.push(inner_column1_arr);

	/*
	 *		MOST HASHTAG TWEET
	 * */

	inner_column2_arr.push('data1');
	inner_label2_arr.push('x');

	most_hashtag_tweet = result.most_hashtag_tweet;
	for (i=0; i <= 10; i++){
		label = most_hashtag_tweet[i][0];
		value = most_hashtag_tweet[i][1];
		inner_column2_arr.push(value);
		inner_label2_arr.push(label);
	}

	most_hashtag_tweet_arr.push(inner_label2_arr);
	most_hashtag_tweet_arr.push(inner_column2_arr);

	/*
	 *		SENTIMENT DISTRIBUTION
	 * */

	sentimen_summary = result.sentimen_summary;
	sample_date      = result.sample_date;
	generate_pie_chart(('#sentimentgraph'+sample_date),sentimen_summary);
	//Generate chart using c3js
	var chart = c3.generate({
		bindto : '#most' + sample_date,
		data : {
			x : 'x',
			columns : most_common_tweet_arr,
			type: 'bar',
			names : { data1: 'Most Tweet'}
		},
		axis: {
			x : {
				type : 'categories',
			}
		},
	});	

	//Generate chart using c3js
	var chart = c3.generate({
		bindto : '#hashtag' + sample_date,
		data : {
			x : 'x',
			columns : most_hashtag_tweet_arr,
			type: 'bar',
			names : { data1: 'Most Hashtag Tweet'}
		},
		axis: {
			x : {
				type : 'categories',
			}
		},
	});

}

get_sentiment_summary = function()
{
	AJAX_SERVER(
		get_sentiment_summary_CALLBACK,
		"GET",
		"api_get_sentiment_analysis_summary_url",
		{},
		true
	)
}

get_sentiment_summary_CALLBACK = function(msg_json)
{
	var most_common_tweet_arr  = [];
	var most_hashtag_tweet_arr = [];

	var inner_column1_arr = [];
	var inner_label1_arr = [];

	var inner_column2_arr = [];
	var inner_label2_arr = [];

	/*
	 *		MOST COMMON TWEET
	 * */
	inner_column1_arr.push('data1');
	inner_label1_arr.push('x');

	console.log(msg_json);
	result = msg_json.result;

	most_common_tweet = result.most_common_tweet;
	console.log(most_common_tweet);
	for (i = 0; i < most_common_tweet.length; i++){
		label = most_common_tweet[i][0];
		value = most_common_tweet[i][1];
		inner_column1_arr.push(value);
		inner_label1_arr.push(label);
	};

	most_common_tweet_arr.push(inner_label1_arr);
	most_common_tweet_arr.push(inner_column1_arr);

	/*
	 *		MOST HASHTAG TWEET
	 * */

	inner_column2_arr.push('data1');
	inner_label2_arr.push('x');

	most_hashtag_tweet = result.most_hashtag_tweet;
	for (i=0; i < most_hashtag_tweet.length; i++){
		label = most_hashtag_tweet[i][0];
		value = most_hashtag_tweet[i][1];
		inner_column2_arr.push(value);
		inner_label2_arr.push(label);
	}

	most_hashtag_tweet_arr.push(inner_label2_arr);
	most_hashtag_tweet_arr.push(inner_column2_arr);

	/*
	 *		SENTIMENT DISTRIBUTION
	 * */

	sentimen_summary = result.sentimen_summary;
	generate_donut_chart('#sentiment_summary',sentimen_summary);
	//Generate chart using c3js
	var chart = c3.generate({
		bindto : '#common_summary',
		data : {
			x : 'x',
			columns : most_common_tweet_arr,
			type: 'bar',
			names : { data1: 'Most Tweet'}
		},
		axis: {
			x : {
				type : 'categories',
			}
		},
	});	

	//Generate chart using c3js
	var chart = c3.generate({
		bindto : '#hashtag_summary',
		data : {
			x : 'x',
			columns : most_hashtag_tweet_arr,
			type: 'bar',
			names : { data1: 'Most Hashtag Tweet'}
		},
		axis: {
			x : {
				type : 'categories',
			}
		},
	});

}



generate_pie_chart = function(output,data)
{
	console.log(data);
	positive = data.positive;
	neutral  = data.neutral;
	negative = data.negative;

	sentiment_data = []
	sentiment_inner_arr1 = [];
	sentiment_inner_arr1.push('data1');
	sentiment_inner_arr1.push(positive);
	sentiment_inner_arr2 = [];
	sentiment_inner_arr2.push('data2');
	sentiment_inner_arr2.push(neutral);
	sentiment_inner_arr3 = [];
	sentiment_inner_arr3.push('data3');
	sentiment_inner_arr3.push(negative);

	sentiment_data.push(sentiment_inner_arr1);
	sentiment_data.push(sentiment_inner_arr2);
	sentiment_data.push(sentiment_inner_arr3);

	//Generate chart using c3js
        var chart = c3.generate({
                bindto : output,
                data : {
                        columns: sentiment_data,
                        type: 'pie',
                        colors : {data1 : 'green', data2: '#5DADE2' , data3 : 'red'},
                        names : { data1 : "Positive", data2 : "Neutral", data3: "Negative"}

                },
        });
}

generate_donut_chart = function(output,data)
{
	console.log(data);
	positive = data.positive;
	neutral  = data.neutral;
	negative = data.negative;

	sentiment_data = []
	sentiment_inner_arr1 = [];
	sentiment_inner_arr1.push('data1');
	sentiment_inner_arr1.push(positive);
	sentiment_inner_arr2 = [];
	sentiment_inner_arr2.push('data2');
	sentiment_inner_arr2.push(neutral);
	sentiment_inner_arr3 = [];
	sentiment_inner_arr3.push('data3');
	sentiment_inner_arr3.push(negative);

	sentiment_data.push(sentiment_inner_arr1);
	sentiment_data.push(sentiment_inner_arr2);
	sentiment_data.push(sentiment_inner_arr3);

	//Generate chart using c3js
        var chart = c3.generate({
                bindto : output,
                data : {
                        columns: sentiment_data,
                        type: 'donut',
                        colors : {data1 : 'green', data2: '#5DADE2' , data3 : 'red'},
                        names : { data1 : "Positive", data2 : "Neutral", data3: "Negative"}

                },
		donut:{
			title : "Sentiment Result",
		}
        });
}



AJAX_SERVER = function(callback_func, method, wservice, uri, bool)
{
        var jqxhr = $.ajax(
        {
                url      : wservice ,
                method   : method   ,
                data     : uri      ,
                dataType : "json"
        }).done(
                function(msg_json)
                {
                        callback_func(msg_json);
                }
        ).fail(
                function(msg_json)
                {
                        callback_func(msg_json);
                }
        ).always(
                function()
                {
                }
        );
}

