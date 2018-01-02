import re
import requests


class SimpleBankResource:
    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs.get(key))

    def create(self):
        raise NotImplemented

    def update(self):
        raise NotImplemented

    def delete(self):
        raise NotImplemented


class Goal(SimpleBankResource):
    __slots__ = [
        'account_ref',
        'amount',
        'archived',
        'color',
        'contributed_amount',
        'created',
        'entry_ids',
        'finish',
        'highlightRgba',
        'id',
        'locked',
        'modified',
        'name',
        'paused',
        'protected',
        'rgba',
        'seq',
        'start',
        'target_amount',
        'user_id'
    ]


class Simple:
    def __init__(self, *args, **kwargs):
        self.session = requests.Session()
        self.session.headers = {"User-Agent": "Mozilla/5.0"}

        self.baseUrl = "https://bank.simple.com"
        self.signInUrl = "https://signin.simple.com"
        
        response = self.session.get(self.signInUrl)
        self.csrf = re.search('<meta name="_csrf" content="(.*)">', response.text).group(1)
        
        payload = {
            "username":  kwargs.get("username"),
            "password": kwargs.get("password"),
            "_csrf":  self.csrf
        }

        response = self.session.post(self.signInUrl, data=payload)

        too_many_attempts = re.search('Too many attempts, try again later.', response.text)

        if too_many_attempts:
            raise Exception("Too many attempts. Fuck.")

        self.partial_auth_token = re.search('<input type="hidden" value="(.*)" name="partial_auth_token" class="optional">', response.text).group(1)

        payload = {
            "_csrf": self.csrf, 
            "partial_auth_token": self.partial_auth_token,
            "pin": pin 
        }

        response = self.session.post("{}/verify".format(self.signInUrl), data=payload)
        response = self.session.get(self.baseUrl)

        self.user_id = re.search('data-uuid="(.*)"', response.text).group(1)
        self.account_id = re.search('data-account-reference="(.*)"', response.text).group(1)

    def get_pin(self):
        pin = input("What is the pin?")
        return pin

    def goals(self):
        goals = []

        url = "{}/goals-api/users/{}/accounts/{}/goals".format(self.baseUrl, self.user_id, self.account_id)
        response = self.session.get(url).json()

        for goal in response:
            goals.append(Goal(**goal))

        return goals 


if __name__ == "__main__":
    simple = Simple(username="", password="")
    active_goals = [goal for goal in simple.goals() if not goal.archived]
    import pdb
    pdb.set_trace()
    print()
