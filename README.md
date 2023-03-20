# Pathy

Pathy is a Pathfinder 2e rules bot for Discord.

Pathy was made using the [Plyable](https://github.com/cjkinni/plyable) python framework.

## Features

- Knows many rules from books published before 2021.
- Rules lookup by name:
  - Any single-word rule or name will be looked up automatically.
  - Any multi-word rule or name can be looked up by enclosing it in double square brackets, e.g. `[[affix a talisman]]`, or by using dashes instead of spaces, e.g. `avert-gaze`.
  - These include rules published after 2021 (using the FoundryVTT pf2e data.)

## Installation

1. Setup a discord bot, and invite it to your server.  It will need some permissions, including the ability to read and send messages.
2. Set your Discord bot token as the `DISCORD_TOKEN` environment variable.
3. Create a 'pathy' channel in your server for the bot to live in.  Currently, pathy will only talk in the #pathy channel; this will  become configurable in the future.
4. Get an OpenAI API key, and set the `OPENAI_API_KEY` environment variable to it.
5. Install the dependencies with `pip install -r requirements.txt`.
6. Run `git submodule update --init --recursive` to download the pf2e data.
6. Run the bot with `python pathy.py`.

## FAQ

### Why is the bot so slow?

ChatGPT-3 is a slow model sometimes.  It's not uncommon for the bot to take 10-20 seconds to respond.  This is a limitation of the model, not the bot.

### Why is the bot not starting up?

Ensure your `DISCORD_TOKEN` and `OPENAI_API_KEY` environment variables are set before running the bot.

### Why doesn't the bot know about the rules from the latest book?

The bot is using ChatGPT, which is only trained on data from before 2021.  The bot manually attempts to get additional context by providing metadata about rules specifically mentioned in the question, but this is not always successful.

### How can I improve the bot to make it better for my particular group?

`system_message.md` contains all the context the bot gets about the rules.  You can edit this file to add additional context, or to change the way the bot responds to certain rules.  The bot needs to be restarted for changes to take effect.

## License

 - Game system information and mechanics are licensed under the Open Game License (OPEN GAME LICENSE Version 1.0a).
 - Any code or data not covered by the above licenses is licensed under the AGPLv3 license.