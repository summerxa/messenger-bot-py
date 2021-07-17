# messenger-bot-py
A Discord bot, written in Python, that allows users in one server to send messages to another.

## Installing Build Dependencies
* Python 3.5.3 or higher
* [Install discord.py](https://discordpy.readthedocs.io/en/latest/intro.html#installing)

## Using the bot
* Create a bot and add it to multiple Discord servers - give it permission to send messages and embed links.
  * Refer to [the docs](https://discordpy.readthedocs.io/en/latest/quickstart.html) for information on connecting the code to a bot.
* Locally, in the same directory as mainCode.py, create a .env file (to store the bot's token) and json file (to store server-related information).
  * .env file should be formatted like this: `DISCORD_TOKEN=[bot's token here]`
  * Change the filename (the one in quotes) in this line to the name of your json file: `config_path = os.path.join(base_path, "server_info.json")`
* Run the code on an editor and keep it running for as long as you want to use the bot.
* Back on Discord, in a channel that the bot can access, send a message starting with "m!send" to send a message to another server or "m!mail" to see messages that other servers have sent to yours.
  * When sending a message, you'll need the ID of the server you're sending a message to, but you can use "m!list" to get a list of all the servers the bot is in and their IDs.
* You can also send "m!help" to view every command the bot responds to.
