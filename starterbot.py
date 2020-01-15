import os
import time
import re
from slackclient import SlackClient
import requests

# instantiate Slack client
# Get this BOT_USER_OAUTH_ACCESS_TOKEN shit here: https://api.slack.com/apps
slack_client = SlackClient(os.environ.get('BOT_USER_OAUTH_ACCESS_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "pika"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Finds and executes the given command, filling in response
    response = None

    image_definitions = get_image_definitions()
    if image_definitions[command]:
        response = image_definitions[command]
    
    if response is None:
        response = "That's not a valid image dummy..."

    attachments = [
        {
            "title": command,
            "image_url": response
        }
    ]

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=command,
        attachments=attachments
    )

def get_image_definitions():
    image_definitions = {}
    r = requests.get('https://raw.githubusercontent.com/jbccollins/images/master/images.text')
    for line in r.iter_lines():
        if line:
            split = line.split()
            image_definitions[split[0]] = split[1]
    return image_definitions
            


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
