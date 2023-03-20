import discord
import os
from plyable import Plyable
import glob
import json
import string
import openai


class PathyPly(Plyable):
    def search_db(self, text):
        # Look for the text in the database.
        # The database is contained in multiple directories under
        # the path './pf2e/packs/data'.
        # The relevant file will be named text.json.
        # If text has spaces, they will be replaced with dashes.
        # We should check all subdirectories until we find one result.

        # Find all the files under the path './pf2e/packs/data'.
        files = []

        text = text.replace(" ", "-").lower()
        if db_by_name.get(text, None) != None:
            return db_by_name[text]

        return None

    @staticmethod
    def clean_nones(value):
        """
        Recursively remove all None values from dictionaries and lists, and returns
        the result as a new dictionary or list.
        """
        if isinstance(value, list):
            return [
                PathyPly.clean_nones(x)
                for x in value
                if x is not None and x != "" and x != {} and x != []
            ]
        elif isinstance(value, dict):
            return {
                key: PathyPly.clean_nones(val)
                for key, val in value.items()
                if val is not None
                and val != ""
                and val != {}
                and val != []
                and key != "img"
                and key != "_id"
                and key != "sourceId"
                and key != "sort"
                and key != "uuid"
                and not (key == "description" and len(str(value)) > 1000)
            }
        else:
            return value

    @staticmethod
    def get_db_items():
        db = {}
        db_by_name = {}
        pattern = f"./pf2e/packs/data/**/*.json"
        for fname in glob.glob(pattern, recursive=True):
            if os.path.isfile(fname):
                # filename without extension:
                name = os.path.splitext(os.path.basename(fname))[0]
                jsond = json.load(open(fname, "r"))
                type = jsond.get("type", "unknown")
                if db.get(type, None) == None:
                    db[type] = {}

                # We keep re-cleaning the json until it stops changing.
                length = -1
                while length != json.dumps(jsond):
                    length = json.dumps(jsond)
                    jsond = PathyPly.clean_nones(jsond)
                json_str = json.dumps(jsond)

                db[type][name] = {"fname": fname, "body": json.dumps(jsond)}
                db_by_name[name] = json.dumps(jsond)

        return db, db_by_name

    def __init__(self, channel_id):
        super().__init__()
        self.channel_id = channel_id
        self.system_message = open("./system_message.md", "r").read()


@PathyPly.on_input_message
def on_input_message(self, message):
    print(f"input from {self.channel_id}: ", message)


@PathyPly.on_input_message
def add_context(self, message):
    warnings = []
    suffix = ""
    punctuation_to_remove = string.punctuation.replace("-", "")
    unpunctuated_message = message.lower().translate(
        str.maketrans("", "", punctuation_to_remove)
    )

    words_with_info = []
    for word in unpunctuated_message.split(" "):
        ignore_list = ["called", "i"]
        if word in ignore_list:
            continue

        if db_by_name.get(word, None) != None:
            relevant_data = db_by_name[word]
            words_with_info.append(word)
            suffix += f'Here\'s up to date rules on "{word}": {relevant_data}\n\n'

    while message.find("[[") != -1:
        # Get the index of the first [[:
        start_index = message.find("[[")
        # Get the index of the first ]]:
        end_index = message.find("]]")
        # Get the text between the [[ and ]]:
        text = message[start_index + 2 : end_index]
        # Replace the text between the [[ and ]]: with the text: [[text]]
        message = message.replace(f"[[{text}]]", text)

        # Look up the text in the pf2e knowledge base.
        relevant_data = self.search_db(text)
        if relevant_data == None:
            warnings += [f"No data found for {text}"]
        else:
            words_with_info.append(text)
            suffix += f'Here\'s up to date rules on "{text}": {relevant_data}\n\n'

    message += str(suffix).strip()

    return message


@PathyPly.on_output_message
def on_output_message(self, message):
    print(f"output to {self.channel_id}: ", message)


class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        self.sessions = {}
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        # Only respond if the channel is pathy, or it's a DM:
        if (
            message.channel.type == discord.ChannelType.private
            or message.channel.name == "pathy"
        ):
            if message.channel.id not in self.sessions:
                self.sessions[message.channel.id] = PathyPly(message.channel.id)

            response = self.sessions[message.channel.id].send(message.content)
            if response:
                await message.channel.send(response)


# This is ugly, move it to a Singleton class.
global db, db_by_name
db, db_by_name = PathyPly.get_db_items()

intents = discord.Intents.default()
intents.message_content = True

client = DiscordClient(intents=intents)
client.run(os.getenv("DISCORD_TOKEN"))
