import time
import telebot
import logging
from dotenv import load_dotenv
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from databaseSync import getNewArticles
from scrapePage import getPageData
from gptStuff import sendToGpt
import threading

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
CHANNEL_ID = os.getenv('CHANNEL_ID')

if not BOT_TOKEN or not USER_ID or not CHANNEL_ID:
    raise ValueError("BOT_TOKEN, USER_ID, or CHANNEL_ID is not set in the environment variables.")

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Runtime queue to store articles awaiting moderation
moderation_queue = []

def sendArticleToModerator(articleContent, image_url, article_id):
    """Send an article's content and image to the moderator with Yes/No buttons."""
    try:
        # Create an inline keyboard with Yes and No buttons
        markup = InlineKeyboardMarkup()
        yes_button = InlineKeyboardButton("✅ Yes", callback_data=f"approve_{article_id}")
        no_button = InlineKeyboardButton("❌ No", callback_data=f"reject_{article_id}")
        markup.add(yes_button, no_button)

        # Send the image with the caption and buttons
        if image_url and not image_url.startswith("data:"):  # Skip base64 images
            sent_message = bot.send_photo(USER_ID, image_url, caption=articleContent, reply_markup=markup)
        else:
            # If no valid image URL, send only the text with buttons
            sent_message = bot.send_message(USER_ID, articleContent, reply_markup=markup)

        # Log sent message with its ID
        logging.info(f"Sent article (ID: {article_id}) to moderator. Message ID: {sent_message.message_id}")

        # Add entire message object to the moderation_queue for later processing
        moderation_queue.append({
            "id": article_id,
            "content": articleContent,
            "image_url": image_url,
            "message": sent_message  # Store entire message object here
        })

    except Exception as e:
        logging.error(f"Failed to send article to moderator: {e}")

def publishArticleToChannel(articleContent, image_url):
    """Publish an approved article to the channel."""
    try:
        # Send the image with the caption to the channel
        if image_url and not image_url.startswith("data:"):  # Skip base64 images
            bot.send_photo(CHANNEL_ID, image_url, caption=articleContent)
        else:
            # If no valid image URL, send only the text
            bot.send_message(CHANNEL_ID, articleContent)

        logging.info("Published article to channel.")
    except Exception as e:
        logging.error(f"Failed to publish article to channel: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Handle Yes/No button clicks, remove buttons, and delete the message."""
    try:
        action, article_id = call.data.split("_")
        article_id = int(article_id)

        logging.info(f"Received callback for action: {action}, article_id: {article_id}, message_id: {call.message.message_id}")

        # Find the article by article_id from the queue
        article_to_process = next((article for article in moderation_queue if article["id"] == article_id), None)

        if article_to_process:
            logging.info(f"Found article (ID: {article_id}) with matching article_id.")

            if action == "approve":
                publishArticleToChannel(article_to_process["content"], article_to_process["image_url"])
                bot.answer_callback_query(call.id, "✅ Article approved and published!")
            elif action == "reject":
                bot.answer_callback_query(call.id, "❌ Article rejected and discarded!")

            # Remove article from queue
            logging.info(f"Removing article (ID: {article_id}) from queue.")
            moderation_queue.remove(article_to_process)

            # Delete the message that the button was clicked on
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            logging.info(f"Deleted message (ID: {call.message.message_id})")

        else:
            bot.answer_callback_query(call.id, "⚠️ Article not found in queue.")
            logging.error(f"Error: Could not find article with article_id: {article_id} in queue.")

    except Exception as e:
        logging.error(f"Error handling callback: {e}")
        bot.answer_callback_query(call.id, "An error occurred. Please try again.")

def start_bot_polling():
    """Start bot polling in a separate thread."""
    while True:
        try:
            bot.polling(none_stop=True, timeout=5)
        except Exception as e:
            logging.error(f"Telegram polling error: {e}")
            time.sleep(5)  # Wait before retrying

def main():
    """Main function to run the bot without blocking new article checks."""
    logging.info("Bot started and running...")

    # Run bot polling in a separate thread
    polling_thread = threading.Thread(target=start_bot_polling, daemon=True)
    polling_thread.start()

    try:
        while True:
            try:
                # Fetch new articles
                new_articles = getNewArticles()
                if not new_articles:
                    logging.info("No new articles found.")
                else:
                    logging.info(f"Found {len(new_articles)} new articles.")
                    for article in new_articles:
                        article_content = getPageData(article["link"])
                        if not article_content:
                            logging.error(f"Failed to scrape content for article: {article['title']}")
                            continue

                        # Process article content using GPT
                        processed_text = sendToGpt(article_content)
                        image_url = article.get("image_link", "")

                        # Store articles with a unique ID
                        article_id = len(moderation_queue)  # Unique index
                        logging.info(f"Adding article (ID: {article_id}) to moderation queue.")
                        moderation_queue.append({
                            "id": article_id,
                            "content": processed_text,
                            "image_url": image_url
                        })

                        # Send for moderation with the unique ID
                        sendArticleToModerator(processed_text, image_url, article_id)

            except Exception as e:
                logging.error(f"Error during article check: {e}")

            time.sleep(5)  # Keep checking for new articles

    except KeyboardInterrupt:
        logging.info("Bot stopped gracefully.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        logging.info("Exiting program.")

if __name__ == "__main__":
    main()
