from flask import Flask, render_template, request, send_from_directory
from flask_misaka import Misaka
import os
import re
import glob
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

Misaka(app)

import os.path

def get_post_data():
    post_files = glob.glob("posts/*.md")
    post_files.sort(key=os.path.getctime, reverse=True)
    posts = []

    for file in post_files:
        with open(file, "r") as f:
            content = f.read()
            raw_title = os.path.basename(file)[:-3]
            date_created = re.search(r'\d{4}-\d{2}-\d{2}', raw_title).group()
            increment = re.search(r'_blog_post_(\d+)', raw_title)
            increment = int(increment.group(1)) if increment else 0

            formatted_date = datetime.strptime(date_created, '%Y-%m-%d').strftime('%d-%m-%Y')
            formatted_title = f"{formatted_date}"
            if increment:
                formatted_title += f" ({increment})"
            else:
                formatted_title += f""

            post = {
                "title": formatted_title,
                "content": content,
                "date_created": datetime.strptime(date_created, '%Y-%m-%d'),
                "increment": increment
            }
            posts.append(post)

    return posts

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
