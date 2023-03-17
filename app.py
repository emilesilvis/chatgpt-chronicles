from flask import Flask, render_template, request, send_from_directory
from flask_misaka import Misaka
import os
import re
import glob
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    # region_name=os.environ.get('AWS_REGION')
)

app = Flask(__name__, static_url_path='/static')

Misaka(app)

import os.path

import re

def parse_title(title):
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', title)
    increment_match = re.search(r'_(\d+)\.', title)
    post_date, increment = None, None
    if date_match:
        post_date = date_match.group(1)
    if increment_match:
        increment = increment_match.group(1)
    return post_date, title, increment

def get_post_data():
    bucket_name = 'chatgpt-chronicles'
    # prefix = 'posts/'

    try:
        post_objects = s3.list_objects_v2(Bucket=bucket_name)
        post_data = []
        for obj in post_objects.get('Contents', []):
            if obj['Key'].lower().endswith('.md'):
                raw_title = os.path.basename(obj['Key'])[:-3]
                post_date, title, increment = parse_title(raw_title)
                post_content = s3.get_object(Bucket=bucket_name, Key=obj['Key'])['Body'].read().decode('utf-8')
                post_data.append({
                    'raw_title': raw_title,
                    'title': title,
                    'date': post_date,
                    'increment': increment,
                    'content': post_content
                })

        post_data.sort(key=lambda x: (x['date'], x['increment']), reverse=True)
        return post_data

    except NoCredentialsError:
        print("No AWS credentials found")
        return []

import os

def get_prompt_data():
    prompt_folder = "static/prompts"
    prompt_files = sorted(os.listdir(prompt_folder))
    prompts = []
    for file in prompt_files:
        if file.lower().endswith('.md'):
            with open(os.path.join(prompt_folder, file), 'r') as f:
                content = f.read()
                prompts.append({"title": file[:-3], "content": content, "filename": os.path.join("prompts", file)})
    return prompts

@app.route('/')
def main():
    posts = get_post_data()
    latest_post = posts[0] if posts else None
    return render_template('index.html', latest_post=latest_post, posts=posts)

@app.route('/post/<post_title>')
def post(post_title):
    posts = get_post_data()
    selected_post = next((post for post in posts if post["title"] == post_title), None)
    return render_template('index.html', latest_post=selected_post, posts=posts)

@app.route('/about/')
def about():
    posts = get_post_data()
    prompts = get_prompt_data()
    return render_template("about.html", posts=posts, prompts=prompts)

if __name__ == '__main__':
    app.run(debug=True)
