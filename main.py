import pickle

import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler

import constant


class MyPickle:
    @staticmethod
    def save(obj, filename):
        with open(filename, "wb") as f:
            pickle.dump(obj, f)

    @staticmethod
    def load(filename):
        with open(filename, "rb") as f:
            try:
                return pickle.load(f)
            except EOFError:
                MyPickle.save(set(), filename)
                return pickle.load(f)


class Home2:
    __slots__ = [
        "api_key",
        "api_secret_key",
        "access_token",
        "access_token_secret",
        "api",
        "data",
    ]

    def __init__(self) -> None:
        self.api_key = constant.API_KEY
        self.api_secret_key = constant.API_SECRET_KEY
        self.access_token = constant.ACCESS_TOKEN
        self.access_token_secret = constant.ACCESS_TOKEN_SECRET
        self.api = self.get_api()
        self.data: set[int] = MyPickle.load("data.pkl")

    def get_api(self) -> tweepy.API:
        auth = tweepy.OAuthHandler(self.api_key, self.api_secret_key)
        auth.set_access_token(self.access_token, self.access_token_secret)
        return tweepy.API(auth)

    def get_random_user_ids(self) -> set[int]:
        tweets = self.api.search_tweets(
            q="-filter:retweets -filter:replies",
            count=50,
            lang="ja",
        )
        return {tweet.user.id for tweet in tweets}

    def update_added_user_ids(self, user_ids) -> None:
        self.data.update(user_ids)
        MyPickle.save(self.data, "data.pkl")

    def add_list_members(self, list_id) -> None:
        filtered_user_ids = self.get_random_user_ids().difference(self.data)
        self.api.add_list_members(list_id=list_id, user_id=filtered_user_ids)
        self.update_added_user_ids(filtered_user_ids)

    def remove_all_list_members(self, list_id) -> None:
        members = self.api.get_list_members(list_id=list_id)
        member_ids = [member.id for member in members]
        self.api.remove_list_members(list_id=list_id, user_id=member_ids)

    # for scheduler
    def update_home2(self) -> None:
        list_id = constant.HOME2_LIST_ID
        self.remove_all_list_members(list_id=list_id)
        self.add_list_members(list_id=list_id)


if __name__ == "__main__":
    scheduler = BlockingScheduler({"apscheduler.timezone": "Asia/Tokyo"})
    scheduler.add_job(Home2().update_home2, "cron", hour=0)
    scheduler.start()
