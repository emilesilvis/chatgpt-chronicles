import requests
from bs4 import BeautifulSoup
import openai
from datetime import datetime
import os
import boto3

# Replace with your OpenAI API key
openai.api_key = os.environ.get("OPENAI_KEY")

# Get the first link from the 'Best' page on Hacker News
url = "https://news.ycombinator.com/best"
response = requests.get(url)
soup = BeautifulSoup(response.text, "lxml")
first_link = soup.find("span", class_="titleline").find("a")["href"]

# Visit the first link and extract text
response = requests.get(first_link)
soup = BeautifulSoup(response.text, "lxml")
text = ' '.join([p.get_text() for p in soup.find_all("p")])

# Send the text to ChatGPT via the OpenAI API to generate a blog post with strong opinions
response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=f"Write a 500-word blog post with strong opinions discussing the following information:\n\n{text}",
    max_tokens=800,  # Increasing max_tokens to accommodate a longer blog post
    n=1,
    stop=None,
    temperature=0.7,
)

# Extract the blog post
blog_post = response.choices[0].text.strip()

# Create a "posts" directory if it doesn't already exist
os.makedirs("posts", exist_ok=True)

# Save the blog post to a Markdown file with today's date and an incrementing number in the title
today = datetime.now().strftime("%Y-%m-%d")
increment = 1

while True:
    filename = f"{today}_blog_post_{increment}.md"
    file_path = os.path.join("posts", filename)
    if not os.path.exists(file_path):
        break
    increment += 1

with open(file_path, "w", encoding="utf-8") as file:
    file.write(blog_post)

print(f"Blog post saved to {file_path}")

# Save the blog post to an S3 bucket
s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
)

s3_bucket = os.environ.get('S3_BUCKET')
s3_key = f"{filename}"

with open(file_path, "rb") as file:
    s3.upload_fileobj(file, s3_bucket, s3_key)

print(f"Blog post uploaded to S3 bucket '{s3_bucket}' with key '{s3_key}'")
