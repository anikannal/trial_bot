import pandas as pd
import psycopg2
import tweepy
import os 
from dotenv import load_dotenv


class TwitterHandler:

    def __init__(self):
        
        load_dotenv('.env')
        ## get the twitter api handle
        CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
        #CONSUMER_KEY = 'tj2MHMY3MnHmyqiRPLOZIKZ3z'
        CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
        #'k0qzJ3ZKyTAVna4TipLyCfwkaaluX40qTMDuxF7iZJzYLZ9dNh'
        ACCESS_KEY = os.environ['TWITTER_ACCESS_KEY']
        #'1395235059087544323-Ofa3VCul9S2jdB5UTwfMKmFrKOsvPJ'
        ACCEES_SECRET = os.environ['TWITTER_ACCESS_SECRET']
        #'eBlz1J8pbpmrC4dd4xJVPxd2M5K8lV5b3qDtJxD7Mh8Hx'
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCEES_SECRET)
        self.api = tweepy.API(auth)

        ## get the database handle
        DATABASE_URL = os.environ['DATABASE_URL']
        self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        ## set number of tweets to retrieve
        self.COUNT = 10

        ## create the dataframes
        self.df_accounts_list = self.postgresql_to_dataframe('select * from accounts_list', ['twitter_account','latest_tweet_id','tweet_ids'])
        #print(self.df_accounts_list)
        self.df_guild_channel = self.postgresql_to_dataframe('select * from guild_channel', ['guild','channel','twitter_accounts','count'])
        #print(self.df_guild_channel)
    
    def set_count(self,guild,channel,count=0):
        ## sets the number of tweets to retrieve
        ## configurable for each guild and channel (arguments) combination
        ## if count (argument) not provided, it returns the current value of the COUNT

        cursor = self.conn.cursor()

        count_guild_channel = int(self.df_guild_channel['count'][(self.df_guild_channel['guild'] == guild)&(self.df_guild_channel['channel']==channel)].values)

        if count < 0:
            return 'Invalid value for tweets to retrieve.\nEnter a number from 1 to 10.\nThe current number of tweets to retrieve is '+str(count_guild_channel)+'.'
        elif count == 0:
            return 'The current number of tweets to retrieve is '+str(count_guild_channel)+'.\n Enter a number from 1 to 10 to change the value.'
        elif count > 10:
            return 'That is too many! enter a number less than or equal to 10.\nThe current number of tweets to retrieve is '+str(count_guild_channel)+'.'
        else:
            self.df_guild_channel['count'][(self.df_guild_channel['guild']==guild)&(self.df_guild_channel['channel']==channel)] = count
            s = "UPDATE guild_channel SET count = "+ str(count) + " WHERE guild = '" + guild + "' AND channel = '" + channel + "';"
            cursor.execute(s)
            self.conn.commit()
            cursor.close()
            return 'Number of tweets to retrieve changed to '+ str(count_guild_channel)+'.'
    
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

    def refresh_tweets(self,account_name=0):
        ## refreshes the tweet store

        tweet_id_list = ''
        cursor = self.conn.cursor()
        if account_name == 0:
            for account_name in self.get_follow_handles():
                latest_tweet_id = self.df_accounts_list['latest_tweet_id'][self.df_accounts_list['twitter_account']==account_name].values
                if latest_tweet_id == '':
                    public_tweets = self.api.user_timeline(account_name,count=self.COUNT)
                else:
                    public_tweets = self.api.user_timeline(account_name,since_id=int(latest_tweet_id),count=self.COUNT)

                for tweet in public_tweets:
                    if len(tweet_id_list)==0:
                        tweet_id_list = str(tweet.id)
                    else:
                        tweet_id_list = tweet_id_list + "," + str(tweet.id)
                ## update tweet_ids in the accounts_list dataframe
                #print(self.df_accounts_list['tweet_ids'][(self.df_accounts_list['twitter_account'] == account_name)])
                self.df_accounts_list['tweet_ids'][(self.df_accounts_list['twitter_account'] == account_name)] = tweet_id_list
                #print(self.df_accounts_list['latest_tweet_id'][(self.df_accounts_list['twitter_account'] == account_name)])
                self.df_accounts_list['latest_tweet_id'][(self.df_accounts_list['twitter_account'] == account_name)] = public_tweets[0].id
                ## append the twitter_accounts array in the guild_channel table
                s = "UPDATE accounts_list SET tweet_ids = '"+ tweet_id_list + "' WHERE twitter_account = '" + account_name + "';"
                cursor.execute(s)
                self.conn.commit()
                cursor.close()
        else:
            
            latest_tweet_id = self.df_accounts_list['latest_tweet_id'][self.df_accounts_list['twitter_account']==account_name].values
            if latest_tweet_id == '':
                public_tweets = self.api.user_timeline(account_name,count=self.COUNT)
            else:
                public_tweets = self.api.user_timeline(account_name,since_id=int(latest_tweet_id),count=self.COUNT)
            
            for tweet in public_tweets:
                if len(tweet_id_list)==0:
                    tweet_id_list = str(tweet.id)
                else:
                    tweet_id_list = tweet_id_list + "," + str(tweet.id)
            #print(tweet_id_list)
            ## update tweet_ids in the accounts_list dataframe
            #print(self.df_accounts_list['tweet_ids'][(self.df_accounts_list['twitter_account'] == account_name)])
            self.df_accounts_list['latest_tweet_id'][(self.df_accounts_list['twitter_account'] == account_name)] = public_tweets[0].id 
            #print(self.df_accounts_list['latest_tweet_id'][(self.df_accounts_list['twitter_account'] == account_name)])
            self.df_accounts_list['tweet_ids'][(self.df_accounts_list['twitter_account'] == account_name)] = tweet_id_list
            #self.df_accounts_list.loc[(self.df_accounts_list['twitter_account'] == account_name)] = [account_name,tweet_list[0],tweet_list[:]]
            #print(self.df_accounts_list)

            s = "UPDATE accounts_list SET tweet_ids = '"+ tweet_id_list + "' WHERE twitter_account = '" + account_name + "';"
            cursor.execute(s)
            self.conn.commit()
            cursor.close()


    def add_account(self,account_name,guild,channel=0):
        ## adds account_name (argument) to the list of twitter handles being followed by guild and channel (arguments)
        
        cursor = self.conn.cursor()

        accounts_list = self.get_follow_handles()
        follow_list = self.get_follow_handles(guild,channel)

        if accounts_list == 0:
            response = 'You are the first one!'
        elif account_name not in accounts_list:
            ## insert account into the dataframe
            self.df_accounts_list.loc[len(self.df_accounts_list.index)] = [account_name, '', '']
            #print(self.df_accounts_list)
            ## insert account into the db table
            ## add name to the accounts_list table
            s = "INSERT INTO accounts_list(twitter_account,latest_tweet_id,tweet_ids) VALUES ('"+account_name+"','0',array['']);"
            #s = "INSERT INTO accounts_list(twitter_account,latest_tweet_id,tweet_ids) VALUES ("+account_name+",\"0\",\"array['']\");"
            cursor.execute(s)
            self.conn.commit()
            self.refresh_tweets(account_name)
            response = 'You are now following '+account_name
        

        if follow_list == 0: ## if this guild and channel combination is not present, add it.
            self.df_guild_channel.loc[len(self.df_guild_channel)] = [guild,channel,account_name,5]
            s = "INSERT INTO guild_channel (guild,channel,twitter_accounts,count) VALUES ('"+guild+"','"+channel+"','"+account_name+"',5);"
            cursor.execute(s)
            self.conn.commit()
        elif account_name not in follow_list: ## if this account is not on the follow_list of the guild and channel
            ## append the twitter_accounts array in the guild_channel DataFrame
            self.df_guild_channel['twitter_accounts'][(self.df_guild_channel['guild'] == guild)&(self.df_guild_channel['channel']==channel)] = str(self.df_guild_channel['twitter_accounts'][(self.df_guild_channel['guild'] == guild)&(self.df_guild_channel['channel']==channel)].values[0]) +","+ str(account_name)
            #print(self.df_guild_channel)
            ## append the twitter_accounts array in the guild_channel table
            s = "UPDATE guild_channel SET twitter_accounts = twitter_accounts||','|| '" + str(account_name) + "' WHERE guild = '" + guild + "' AND channel = '" + channel + "';"
            cursor.execute(s)
            self.conn.commit()
            response = 'You are now following '+account_name
        else:
            response = 'You are already following'+account_name

        cursor.close()
        return response

    def get_tweets(self,guild,channel):
        ## returns the tweets for twitter handles being followed by the guild and channel (arguments).
        ## error code 0 - if no accounts are being followed
        ## error code 1 - if no new tweets are found

        list_of_tweets = []
        subset_accounts_list = self.get_follow_handles(guild,channel)
        print('accounts to read')
        print(subset_accounts_list)
        ## return list with '0' if no accounts found
        if subset_accounts_list==0:
            return 0
        ## make a list of all the tweets to share
        for account in subset_accounts_list:
            tweet_ids = self.get_tweet_ids(account)
            print('tweet_ids')
            print(tweet_ids)
            ## convert from tweet_id to a link to the tweet
            if tweet_ids == 0:
                continue
            else:
                count = int(self.df_guild_channel['count'][(self.df_guild_channel['guild'] == guild)&(self.df_guild_channel['channel']==channel)].values)
                tweet_ids = tweet_ids[:count]
                for tweet_id in tweet_ids:
                    list_of_tweets.append("https://twitter.com/"+ account +"/status/"+str(tweet_id))
        ## return the consolidated list of tweets
        if len(list_of_tweets)==0:
            return 1
        return list_of_tweets

    def get_tweet_ids(self,account_name):
        ## returns a list tweet ids for the account_name (argument)
        ## error code 0 - if account is not found 
        
        accounts_list = self.df_accounts_list['twitter_account'].values
        ## check if account is in the accounts list
        if account_name not in accounts_list:
            return 0
        else: 
            ## make a list of all the tweets to share
            tweet_ids = list(str(self.df_accounts_list['tweet_ids'][self.df_accounts_list['twitter_account']==account_name].values[0]).split(","))
            return tweet_ids

    def get_follow_list(self,guild=0,channel=0):
        ## returns a list of links to twitter accounts being followed by guild and channel (arguments)
        ## if guild == 0, returns a list of all twitter handles being followed by all guilds
        ## error code 0 - if guild != 0, guild and channel have not followed any twitter handles yet
        
        links=[]
        handles = self.get_follow_handles(guild,channel)
        ## return list with '0' if no accounts found
        if handles==0:
            return 0
        ## share the list of accounts being followed
        for handle in handles:
            links.append("https://twitter.com/"+handle)
        return links

    def get_follow_handles(self,guild=0,channel=0):
        ## returns a list of tweeter handles being followed by the guild and channel provided in the arguments
        ## if guild == 0, returns a list of all the twitter handles being followed by all guilds
        ## error code 0 - if guild != 0, guild and channel have not followed any twitter handles yet

        handles = []
        ## send all accounts being followed if guild not shared
        if guild==0:
            handles = list(self.df_accounts_list['twitter_account'].values)
        else:
            ## find all the accounts followed by this guild and channel
            guilds = self.df_guild_channel['guild'].values
            print('guilds')
            print(guilds)
            channels = self.df_guild_channel['channel'][self.df_guild_channel['guild']==guild].values
            print('channels')
            print(channels)
            if ((guild in guilds) and (channel in channels)):
                print('inside the if')
                handles = list(str(self.df_guild_channel['twitter_accounts'][(self.df_guild_channel['guild'] == guild)&(self.df_guild_channel['channel'] == channel)].values[0]).split(","))
            else:
                print('didnt make it')
                handles = 0
        return handles
