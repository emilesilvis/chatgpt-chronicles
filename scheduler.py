import subprocess
import schedule
import time

def call_script():
    script_path = "write_blog_post_top_hackernews_post.py"  # Replace with the path to your Python script
    subprocess.run(["python", script_path], check=True)

def main():
    schedule.every().day.at("00:00").do(call_script)  # Set the time you want the script to run daily (e.g., "00:00" for midnight)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute if the scheduled job should be executed

if __name__ == "__main__":
    main()
