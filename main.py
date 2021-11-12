from apscheduler.schedulers.blocking import BlockingScheduler

import constant
from modules.pickle import Pickle
from modules.twitter import Twitter


class Home2:
    __slots__ = ("api", "pickle", "list_id")

    def __init__(self) -> None:
        self.api = Twitter(*constant.TWITTER_CREDENTIALS)
        self.pickle = Pickle(path="data.pkl", default_data=set[int]())
        self.list_id = constant.HOME2_LIST_ID

    def get_list_member_ids(self) -> set[int]:
        count = self.api.get_list(list_id=self.list_id).member_count
        members = self.api.get_list_members(list_id=self.list_id, count=count)
        return set(map(lambda member: member.id, members))

    def get_random_user_ids(self) -> set[int]:
        tweets = self.api.search_tweets(
            "-filter:retweets -filter:replies", count=100, lang="ja"
        )
        return set(map(lambda tweet: tweet.user.id, tweets))

    def remove_all_list_members(self) -> None:
        user_ids = self.get_list_member_ids()
        self.api.remove_list_members(list_id=self.list_id, user_id=user_ids)

    def add_list_members(self) -> None:
        user_ids = self.get_random_user_ids().difference(self.pickle.data)
        self.api.add_list_members(list_id=self.list_id, user_id=user_ids)
        self.update_added_user_ids(user_ids)

    def update_added_user_ids(self, user_ids) -> None:
        self.pickle.data.update(user_ids)
        self.pickle.save()

    def run(self) -> None:
        self.remove_all_list_members()
        self.add_list_members()


if __name__ == "__main__":
    scheduler = BlockingScheduler({"apscheduler.timezone": "Asia/Tokyo"})
    scheduler.add_job(Home2().run, "cron", hour=0)
    scheduler.start()
