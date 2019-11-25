import sqlite3
from urllib.parse import urlsplit
from flask import Flask, render_template, request, jsonify
from database import Database

app = Flask(__name__)

# Routes

@app.route('/')
@app.route('/r/<subreddit>')
def posts(subreddit=None):
    # Get named parameters from url
    days = request.args.get('days')
    limit = request.args.get('limit')
    unread = request.args.get('unread')
    ignore = request.args.get('ignore')

    # Transform and validate parameters
    limit = int(limit) if limit else 200
    unread = 1 if unread == None or unread == '1' else 0
    days = int(days) if days else 10000 if subreddit else 7
    ignore = 1 if ignore == None or ignore == '1' else 0

    # Get posts from database
    with Database() as db:
        if subreddit:
            try:
                posts = db.get_posts_by_subreddit(subreddit, limit, unread, days)
            except ValueError:
                # Subreddit does not exist
                posts = []
        elif ignore:
            posts = db.get_posts_all_unignored(limit, unread, days)
        else:
            posts = db.get_posts_all(limit, unread, days)

    return render_template(
        'posts.html',
        header=subreddit or 'all',
        posts=posts, 
        urlsplit=urlsplit, 
        three_digits=three_digits,
        days=days,
        limit=limit,
        unread=unread,
        ignore=ignore
    )


@app.route('/saved')
def saved():
    subreddit = request.args.get('sr')
    with Database() as db:
        if subreddit:
            posts = db.get_saved_by_subreddit(subreddit)
        else:
            posts = db.get_saved_posts()

    return render_template(
        'saved.html',
        header="Saved",
        posts=posts,
        urlsplit=urlsplit,
        three_digits=three_digits,
        subreddit=subreddit or ''
    )


@app.route('/loved')
def loved():
    subreddit = request.args.get('sr')
    with Database() as db:
        if subreddit:
            posts = db.get_loved_by_subreddit(subreddit)
        else:
            posts = db.get_loved_posts()

    return render_template(
        'saved.html',
        header="Loved",
        posts=posts,
        urlsplit=urlsplit,
        three_digits=three_digits,
        subreddit=subreddit or ''
    )


@app.route('/subreddits')
def subreddits():
    with Database() as db:
        subreddits = db.get_subreddits()
    
    return render_template(
        'subreddits.html',
        subreddits=subreddits
    )


@app.route('/readit/<uid>', methods=['POST'])
def readit(uid):
    success = False
    with Database() as db:
        if db.toggle_readit(uid):
            db.commit()
            success = True

    return jsonify(success=success)

@app.route('/saveit/<uid>', methods=['POST'])
def saveit(uid):
    success = False
    with Database() as db:
        if db.toggle_saved(uid):
            db.commit()
            success = True

    return jsonify(success=success)

@app.route('/loveit/<uid>', methods=['POST'])
def loveit(uid):
    success = False
    with Database() as db:
        if db.toggle_loved(uid):
            db.commit()
            success = True

    return jsonify(success=success)

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r


# Helpers

def three_digits(num):
    """
    Rounds a number to the nearest thousandth and returns a string
    Ex) 54100 becomes "54.1K"
    """
    if int(num) >= 1000:
        thou, hund = divmod(int(num), 1000)
        hund, tens = divmod(hund, 100)
        return "{}.{}K".format(thou, hund)
    else:
        return str(num)