import praw
import sqlite3
import argparse
import json
from threading import Thread
from time import sleep
from database import Database


class App:
    def __init__(self):
        # Read credentials from file
        with open('creds.json') as json_file:
            data = json.load(json_file)

        # Establish API connection
        self.reddit = praw.Reddit(
            client_id=data['client_id'],
            client_secret=data['client_secret'],
            user_agent=data['user_agent']
        )

        # Connect to database
        self.db = Database()

        self.postcount = 0
        self.done = False

    def add_top_from_subreddit(self, sr, limit=None, time='all'):
        """Adds top posts from a specific subreddit to the database"""

        # Add subreddit
        subreddit = self.reddit.subreddit(sr)
        self.db.add_subreddit(subreddit)

        # Add submissions
        for submission in subreddit.top(limit=limit, time_filter=time):
            self.db.add_post(submission, subreddit)
            self.postcount += 1
        
        # commit additions to database
        self.db.commit()
    
    def add_top(self, sr, limit=None, time='all'):
        """
        Adds top posts from any subreddit. Slower than add_top_from_subreddit(), 
        and is intended only for r/all and r/popular.
        """
        # Add subreddit
        subreddit = self.reddit.subreddit(sr)

        # Add submissions
        for submission in subreddit.top(limit=limit, time_filter=time):
            postsubreddit = submission.subreddit
            self.db.add_subreddit(postsubreddit)
            self.db.add_post(submission, postsubreddit)
            self.postcount += 1
            
        self.db.commit()

    def print_progress(self):
        def message():
            return 'Posts added: {}'.format(self.postcount)
        
        while self.done == False:
            print(message(), end='\r')
            sleep(0.25)
        
        print(message())

    def run(self):
        # Parse arguments
        parser = argparse.ArgumentParser(description="Reddit database")
        parser.add_argument('subreddit', type=str, help='The subreddit to search')
        parser.add_argument('limit', type=int, default=1000, nargs='?', help="[optional] Maximum submissions to get (max 1000)")
        parser.add_argument('time', type=str, default='all', nargs='?', help="[optional] Top of x time (hour, day, week, month, year, or all)")
        args = parser.parse_args()

        # Let the user know what operation is being performed
        print("Adding the top posts from /r/{} to database.".format(args.subreddit))
        timestr = "all time" if args.time == 'all' else "the {}".format(args.time) 
        print("Limited to the top {} posts of {}.".format(args.limit, timestr))

        # Start progress bar thread
        progress = Thread(target=self.print_progress, daemon=True)
        progress.start()

        # Add submissions to database
        if args.subreddit == 'all' or args.subreddit == 'popular':
            self.add_top(args.subreddit, args.limit, args.time)
        else:
            self.add_top_from_subreddit(args.subreddit, args.limit, args.time)

        # End progress bar thread and finish
        self.done = True
        progress.join()
        self.db.close()
        print('Done')
         

if __name__ == "__main__":
    app = App()
    app.run()