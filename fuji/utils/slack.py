import requests
from slacker import Slacker
from config import slack_cnf

# Sending message to Slack
# Regarding the library: Slacker: https://github.com/os/slacker/blob/master/slacker/__init__.py
# Regarding incoming-webhooks: https://api.slack.com/incoming-webhooks


def notify_via_bot(text, channel=None, attachments=None, slack_webhook_url=None):
    """
    Text Cheatsheet:
    Mention: <@U024BE7LH> -> ユーザーIDはポイント
    Emoji: :smile:
    :param text:
    :param channel:
    :param attachments:
    :param slack_webhook_url:
    :return:
    """
    if slack_webhook_url is None:
        slack_webhook_url = slack_cnf.slack_webhook_url
    if channel is None:
        channel = slack_cnf.default_channel
    print(slack_webhook_url)
    slack = Slacker('', incoming_webhook_url=slack_webhook_url)
    slack.incomingwebhook.post({
        'channel': channel,
        'text': text,
        'link_names': '1',
        'attachments': attachments
    })


def notify_via_user():
    """
    See: https://api.slack.com/messaging/sending

    :param text:
    :param channel:
    :param slack_user_token:
    :return:
    """

    if slack_user_token is None:
        slack_user_token = slack_cnf.slack_user_token
    post_message_url = 'https://slack.com/api/chat.postMessage'
    headers = {"Authorization": "Bearer " + slack_user_token}
    payload = {
        'channel': channel,
        'as_user': True,
        "text": text
    }
    requests.post(post_message_url, headers=headers, data=payload)
