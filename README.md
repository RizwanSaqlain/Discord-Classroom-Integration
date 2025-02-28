# Classroom Bot

Classroom Bot is a Discord bot that integrates with Google Classroom to manage announcements and coursework. It allows teachers to send announcements and coursework materials directly to a Discord channel.

## Features

- Fetches announcements and coursework from Google Classroom.
- Sends announcements and coursework materials to specified Discord channels.
- Supports searching for announcements and coursework materials.

## Requirements

- Python 3.x
- Discord.py library
- Google API client library
- MySQL connector
- Icecream library

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install the required packages:**
   ```bash
   pip install discord google-api-python-client mysql-connector-python icecream
   ```

3. **Set up Google API credentials:**
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the Google Classroom API.
   - Create OAuth 2.0 credentials and download the `credentials.json` file.
   - Place the `credentials.json` file in the project directory.

4. **Set up the Discord bot:**
   - Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications).
   - Copy the bot token and set it as an environment variable:
     ```bash
     export DISCORD_BOT_TOKEN='your-bot-token'
     ```

5. **Database Setup:**
   - Ensure you have a MySQL database set up and update the connection details in `configuration.py`.

## Usage

- Run the bot:
   ```bash
   python NewBot.py
   ```

- Use the following commands in Discord:
   - `!hello`: The bot will greet you.
   - `!run`: Executes the commands to send announcements and coursework.
   - `!shutdown`: Shuts down the bot.
   - `!search <term>`: Searches for coursework materials by title.
   - `!find <term>`: Searches for announcements by materials.

## License

This project is licensed under the MIT License.
