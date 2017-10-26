# coding: utf-8

from __future__ import print_function, unicode_literals, division


class BotObject(dict):
    def __init__(self, campbot, data):
        super(BotObject, self).__init__(data)
        self._campbot = campbot

        # we must define __setattr__ after _campbot, otherwise it will be stored in dict
        self.__setattr__ = self.__setitem__

    def __getattr__(self, item):
        return self[item]

    def _convert_list(self, name, constructor):
        self[name] = [constructor(self._campbot, data) for data in self[name]]

    def _convert_dict(self, name, constructor):
        self[name] = {key: constructor(self._campbot, self[name][key]) for key in self[name]}


class WikiUser(BotObject):
    def get_contributions(self, oldest_date=None, newest_date=None):
        return self._campbot.wiki.get_contributions(user_id=self.document_id,
                                                    oldest_date=oldest_date,
                                                    newest_date=newest_date)

    def get_last_contribution(self, oldest_date=None, newest_date=None):
        for contribution in self.get_contributions(oldest_date=oldest_date, newest_date=newest_date):
            return contribution

        return None

    def save(self, message):
        payload = {"document": self, "message": message}
        return self._campbot.wiki.put("/profiles/{}".format(self.document_id), payload)


class Route(BotObject):
    def fix_markdown(self, corrector):
        updated = False
        for locale in self.locales:
            for field in ("description", "gear", "remarks", "route_history", "summary"):
                if locale[field]:
                    new_value = corrector(locale[field], field, locale)
                    updated = updated or (new_value != locale[field])
                    locale[field] = new_value

        return updated

    def get_locale(self, lang):
        for locale in self.locales:
            if locale["lang"] == lang:
                return locale

    def save(self, message):
        payload = {"document": self, "message": message}
        return self._campbot.wiki.put("/routes/{}".format(self.document_id), payload)


class ForumUser(BotObject):
    def get_wiki_user(self):
        return self._campbot.wiki.get_user(forum_name=self.username)


class Post(BotObject):
    def __init__(self, campbot, data):
        super(Post, self).__init__(campbot, data)
        self._convert_dict("polls", Poll)


class Poll(BotObject):
    def __init__(self, campbot, data):
        super(Poll, self).__init__(campbot, data)
        self._convert_list("options", PollOption)


class PollOption(BotObject):
    def get_voters(self, post_id, poll_name):
        url = "/polls/voters.json?post_id={}&poll_name={}&option_id={}&offset={}"
        offset = 0
        while True:
            data = self._campbot.forum.get(url.format(post_id, poll_name, self.id, offset))[poll_name]

            if self.id not in data or len(data[self.id]) == 0:
                raise StopIteration
            for voter in data[self.id]:
                yield ForumUser(self._campbot, voter)

            offset += 1