import pandas as pd
import psycopg2
import tweepy
import os 


class TwitterHandler:

    def __init__(self):
        
        ## get the twitter api handle
        CONSUMER_KEY = 'tj2MHMY3MnHmyqiRPLOZIKZ3z'
        CONSUMER_SECRET = 'k0qzJ3ZKyTAVna4TipLyCfwkaaluX40qTMDuxF7iZJzYLZ9dNh'
        ACCESS_KEY = '1395235059087544323-Ofa3VCul9S2jdB5UTwfMKmFrKOsvPJ'
        ACCEES_SECRET = 'eBlz1J8pbpmrC4dd4xJVPxd2M5K8lV5b3qDtJxD7Mh8Hx'
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCEES_SECRET)
        self.api = tweepy.API(auth)

        ## get the database handle
        DATABASE_URL = os.environ['DATABASE_URL']
        self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        ## create the dataframes
        self.df_accounts_list = self.postgresql_to_dataframe('select * from accounts_list', ['twitter_account','latest_tweet_id','tweet_ids'])
        self.df_guild_channel = self.postgresql_to_dataframe('select * from guild_channel', ['guild','channel','twitter_accounts'])

    

    def postgresql_to_dataframe(self,select_query, column_names):
        """
        Tranform a SELECT query into a pandas dataframe
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(select_query)
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            cursor.close()
            return 1
        
        # Naturally we get a list of tupples
        tupples = cursor.fetchall()
        cursor.close()
        
        # We just need to turn it into a pandas dataframe
        df = pd.DataFrame(tupples, columns=column_names)
        return df

    def get_follow_list(self,guild = 0,channel=0):
        ## send all accounts being followed if guild not shared
        if guild==0:
            accounts_list = self.df_accounts_list['twitter_account']
        else:  
            ## find all the accounts followed by this guild and channel
            accounts_list = self.df_guild_channel['twitter_accounts'][(self.df_guild_channel['guild'] == guild)&(self.df_guild_channel['channel'] == channel)]
      
        return list(accounts_list)

    def get_tweet_ids(self,list_of_accounts):
        ## make a list of all the tweets to share
        tweet_ids = []
        for acct in list_of_accounts:
            tweet_ids.append(list(self.df_accounts_list['tweet_ids'][self.df_accounts_list['twitter_account']==acct]))
        return tweet_ids

    def refresh_tweets(self,account_name=0):
        tweet_list=[]
        cursor = self.conn.cursor()
        if account_name == 0:
            for account_name in self.get_follow_list():
                public_tweets = api.user_timeline(account_name)
                for tweet in public_tweets:
                    tweet_list.append(tweet.id)
                ## update tweet_ids in the accounts_list dataframe
                self.df_accounts_list['tweet_ids'][(self.df_accounts_list['twitter_account'] == account_name)] = tweet_list
                self.df_accounts_list['latest_tweet_id'][(self.df_accounts_list['twitter_account'] == account_name)] = tweet_list[0]
                ## append the twitter_accounts array in the guild_channel table
                s = "UPDATE accounts_list SET tweet_ids = array(" + tweet_list + ") WHERE twitter_account = \"" + account_name + "\";"
                cursor.execute(s)
                cursor.commit()
        else:
            public_tweets = api.user_timeline(account_name)
            for tweet in public_tweets:
                tweet_list.append(tweet.id)
            ## update tweet_ids in the accounts_list dataframe
            self.df_accounts_list['tweet_ids'][(self.df_accounts_list['twitter_account'] == account_name)] = tweet_list
            self.df_accounts_list['latest_tweet_id'][(self.df_accounts_list['twitter_account'] == account_name)] = tweet_list[0]
            ## append the twitter_accounts array in the guild_channel table
            s = "UPDATE accounts_list SET tweet_ids = array(" + tweet_list + ") WHERE twitter_account = \"" + account_name + "\";"
            cursor.execute(s)
            cursor.commit()


    def add_account(self,account_name,guild,channel=0):
        
        cursor = self.conn.cursor()

        if account_name not in get_follow_list():
            ## insert account into the dataframe
            self.df_accounts_list.loc[len(self.df_accounts_list.index)] = [account_name, '0', []]
            ## insert account into the db table
            ## add name to the accounts_list table
            s = "INSERT INTO accounts_list(twitter_account,latest_tweet_id,tweet_ids) VALUES (\""+account_name+"\",\"0\",\"[]\");"
            cursor.execute(s)
            cursor.commit()
            self.refresh_tweets(account_name)
        if account_name not in get_follow_list(guild,channel):
            ## append the twitter_accounts array in the guild_channel DataFrame
            self.df_guild_channel['twitter_accounts'][(self.df_guild_channel['guild'] == guild)&(self.df_guild_channel['channel']==channel)] = self.df_guild_channel['twitter_accounts'][(self.df_guild_channel['guild'] == guild)&(self.df_guild_channel['channel']==channel)] + [account_name]
            ## append the twitter_accounts array in the guild_channel table
            s = "UPDATE guild_channel SET twitter_accounts = array_append(twitter_accounts,\"" + str(account_name) + "\") WHERE guild = \"" + guild + "\" AND channel = \"" + channel + "\";"
            cursor.execute(s)
            cursor.commit()
            resonse = 'You are now following '+account_name
        else:
            resonse = 'You are already following'+account_name
        
        return response

    def get_tweets(self,guild, channel):
        list_of_tweets = []
        subset_accounts_list = self.get_follow_list(guild,channel)
        ## make a list of all the tweets to share
        tweet_ids = self.get_tweet_ids(subset_accounts_list)
        ## convert from tweet_id to a link to the tweet
        for tweet_id in tweet_ids:
            list_of_tweets.append("https://twitter.com/"+acct+"/status/"+str(tweet.id))
        return list_of_tweets

    def get_follow_list(self,guild, channel):
        links = []
        ## find all the accounts followed by this guild and channel
        accounts_list = list(self.df_guild_channel['twitter_accounts'][(self.df_guild_channel['guild'] == guild)&(self.df_guild_channel['channel'] == channel)])
        ## share the list of accounts being followed
        for acct in accounts_list:
            links.append("https://twitter.com/"+acct)
        return links