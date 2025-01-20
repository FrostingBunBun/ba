import time
import schedule
import pytz
from datetime import datetime
import telebot
from dotenv import load_dotenv
import os


load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

if not BOT_TOKEN or not USER_ID:
    raise ValueError("BOT_TOKEN or USER_ID is not set in the environment variables.")

bot = telebot.TeleBot(BOT_TOKEN)

WARSAW_TZ = pytz.timezone('Europe/Moscow')

# List of target times in HH:MM format
TARGET_TIMES = ["10:57", "11:00", "15:30", "20:00"]

def sendScheduledMessage():
    try:
        bot.send_message(USER_ID, f"Sent at {datetime.now(WARSAW_TZ)}")
        print("[INFO] Message sent successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")

def checkAndRunTask():
    try:
        now = datetime.now(WARSAW_TZ)
        currentTime = now.strftime("%H:%M")
        print(f"[DEBUG] Current time: {currentTime}")
        
        if currentTime in TARGET_TIMES:
            print(f"[INFO] Target time {currentTime} reached. Sending message.")
            sendScheduledMessage()
        else:
            print(f"[DEBUG] No matching target time. {TARGET_TIMES}")
    except Exception as e:
        print(f"[ERROR] Failed during time check: {e}")

def main():
    """Main function to schedule tasks and run the bot."""
    print("[INFO] Bot started and running...")
    
    # Schedule the time check task every minute
    schedule.every().minute.do(checkAndRunTask)

    try:
        while True:
            try:
                schedule.run_pending()
            except Exception as e:
                print(f"[ERROR] An error occurred while running scheduled tasks: {e}")
            
            time.sleep(1)  # Prevent excessive CPU usage
    except KeyboardInterrupt:
        print("\n[INFO] Bot stopped gracefully.")
    except Exception as e:
        print(f"[CRITICAL] An unexpected error occurred: {e}")
    finally:
        print("[INFO] Exiting program.")

if __name__ == "__main__":
    main()
