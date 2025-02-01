import time
import telebot
from dotenv import load_dotenv
import os
import logging
from databaseSync import getNewArticles  # Import the getNewArticles function from datasync.py
from scrapePage import getPageData  # Import the getPageData function from scrapePage.py

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)

# Load bot token and user ID from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

if not BOT_TOKEN or not USER_ID:
    raise ValueError("BOT_TOKEN or USER_ID is not set in the environment variables.")

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

def sendArticleToChannel(article):
    """Send an article's content to the Telegram channel, truncating it to the first 10 characters."""
    try:
        # Scrape the article's content using scrapePage.py
        articleContent = getPageData(article["link"])
        if not articleContent:
            logging.error(f"Failed to scrape content for article: {article['title']}")
            return

        # Truncate the content to the first 10 characters
        truncatedContent = articleContent[:20] + "..." if len(articleContent) > 10 else articleContent

        # Prepare the message with the title and truncated content
        message = f"**{article['title']}**\n\n{truncatedContent}"

        # Send the message
        bot.send_message(USER_ID, message)
        logging.info(f"Sent article to channel: {article['title']}")

    except Exception as e:
        logging.error(f"Failed to send article to channel: {e}")

def main():
    """Main function to run the bot in an infinite loop."""
    logging.info("Bot started and running...")

    try:
        while True:
            try:
                # Fetch new articles using datasync.py
                newArticles = getNewArticles()
                if not newArticles:
                    logging.info("No new articles found.")
                else:
                    logging.info(f"Found {len(newArticles)} new articles.")
                    for article in newArticles:
                        sendArticleToChannel(article)
            except Exception as e:
                logging.error(f"Error during article check: {e}")

            # Wait for 5 seconds before the next check
            time.sleep(5)
    except KeyboardInterrupt:
        logging.info("Bot stopped gracefully.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        logging.info("Exiting program.")

if __name__ == "__main__":
    main()