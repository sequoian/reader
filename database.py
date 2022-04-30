"""
Database interface
"""
import sqlite3
from time import time

DB_PATH = 'reddit.db'


class Database:
    """Grants access to and provides an interface for the database"""
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """Close database connection"""
        self.conn.close()

    def commit(self):
        """Save database modification"""
        self.conn.commit()

    def init_tables(self):
        """Initialize the database tables"""
        # Subreddits table
        sql = """
            CREATE TABLE IF NOT EXISTS subreddits (
                id text PRIMARY KEY,
                name text NOT NULL,
                ignored integer DEFAULT 0,
                favorite integer DEFAULT 0
            )
        """
        self.cursor.execute(sql)

        # Submissions table
        sql = """
            CREATE TABLE IF NOT EXISTS submissions (
                id text PRIMARY KEY,
                title text NOT NULL,
                created integer NOT NULL,
                score integer NOT NULL,
                url text NOT NULL,
                comments_link text NOT NULL,
                num_comments integer NOT NULL,
                subreddit integer REFERENCES subreddits(id),
                read_it integer DEFAULT 0,
                saved integer DEFAULT 0,
                loved integer DEFAULT 0
            )
        """
        self.cursor.execute(sql)

    def add_post(self, post, subreddit):
        """Adds a submission to the database"""
        sql = """
            INSERT OR IGNORE INTO submissions (
                id, title, created, score, url, comments_link, num_comments, subreddit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
        self.cursor.execute(sql, (
            post.id, post.title, post.created_utc, post.score,
            post.url, post.permalink, post.num_comments, subreddit.id
        ))

        return self.cursor.rowcount

    def add_subreddit(self, subreddit):
        """Adds a subreddit to the database"""
        self.cursor.execute(
            "INSERT OR IGNORE INTO subreddits (id, name) VALUES (?, ?)",
            (subreddit.id, subreddit.display_name)
        )

        return self.cursor.rowcount

    def get_posts_all(self, count_limit=1000, show_read=True, days_limit=100000):
        """Get posts from all subreddits"""
        sql = """
            SELECT *, sr.name AS sr_name FROM (
                SELECT * FROM submissions 
                WHERE (read_it = 0 OR read_it = ?) AND created >= ?
                ORDER BY score DESC LIMIT ?
            ) sm
            JOIN subreddits sr ON sm.subreddit = sr.id
            ORDER BY score DESC
        """
        show_read = 1 if show_read else 0
        created = time() - days_limit * 60 * 60 * 24
        self.cursor.execute(sql, (show_read, created, count_limit))
        return self.cursor.fetchall()

    def get_posts_all_unignored(self, count_limit=1000, show_read=True, days_limit=100000):
        """
        Get posts from all unignored subreddits
        Slower than get_posts_all()
        """
        sql = """
            SELECT * FROM (
                SELECT *, sr.name AS sr_name FROM (
                    SELECT * FROM submissions 
                    WHERE (read_it = 0 OR read_it = ?) AND created >= ?
                    ORDER BY score DESC
                ) sm
                JOIN subreddits sr ON sm.subreddit = sr.id
                ORDER BY score DESC
            )
            WHERE ignored = 0 LIMIT ?
        """
        show_read = 1 if show_read else 0
        created = time() - days_limit * 60 * 60 * 24
        self.cursor.execute(sql, (show_read, created, count_limit))
        return self.cursor.fetchall()

    def get_posts_by_subreddit(self, subreddit, count_limit=1000,
                               show_read=True, days_limit=100000):
        """
        Get posts that belong to a specific subreddit
        """
        # Find the subreddit if it exists
        self.cursor.execute(
            "SELECT * FROM subreddits WHERE name = ? COLLATE NOCASE",
            (subreddit,))
        sub = self.cursor.fetchone()
        if not sub:
            raise ValueError('The subreddit "{}" does not exist'.format(subreddit))

        # Return the matching posts
        sql = """
            SELECT *, sr.name AS sr_name FROM (
                SELECT * FROM submissions 
                WHERE (read_it = 0 OR read_it = ?) 
                AND subreddit = ? AND created >= ?
                ORDER BY score DESC LIMIT ?
            ) sm
            JOIN subreddits sr ON sm.subreddit = sr.id
            ORDER BY score DESC
        """
        show_read = 1 if show_read else 0
        created = time() - days_limit * 60 * 60 * 24
        self.cursor.execute(sql, (show_read, sub['id'], created, count_limit))
        return self.cursor.fetchall()

    def get_saved_posts(self):
        """Get all saved posts"""
        self.cursor.execute("""
            SELECT *, sr.name AS sr_name FROM (
                SELECT * FROM submissions WHERE saved = 1
            ) sm JOIN subreddits sr ON sm.subreddit = sr.id
            ORDER BY sr.name ASC
        """)
        return self.cursor.fetchall()

    def get_saved_by_subreddit(self, subreddit):
        """Get saved posts belonging to a subreddit"""
        self.cursor.execute("""
            SELECT * FROM (
                SELECT *, sr.name AS sr_name FROM (
                    SELECT * FROM submissions WHERE saved = 1
                ) sm 
                JOIN subreddits sr ON sm.subreddit = sr.id
                ORDER BY sr.name ASC
            ) WHERE sr_name = ? COLLATE NOCASE
        """, (subreddit,))
        return self.cursor.fetchall()

    def get_loved_posts(self):
        """Get all loved posts"""
        self.cursor.execute("""
            SELECT *, sr.name AS sr_name FROM (
                SELECT * FROM submissions WHERE loved = 1
            ) sm JOIN subreddits sr ON sm.subreddit = sr.id
            ORDER BY sr.name ASC
        """)
        return self.cursor.fetchall()

    def get_loved_by_subreddit(self, subreddit):
        """Get loved posts belonging to a subreddit"""
        self.cursor.execute("""
            SELECT * FROM (
                SELECT *, sr.name AS sr_name FROM (
                    SELECT * FROM submissions WHERE loved = 1
                ) sm 
                JOIN subreddits sr ON sm.subreddit = sr.id
                ORDER BY sr.name ASC
            ) WHERE sr_name = ? COLLATE NOCASE
        """, (subreddit,))
        return self.cursor.fetchall()

    def get_subreddits(self):
        """Get all subreddits"""
        self.cursor.execute(
            """SELECT * FROM subreddits WHERE ignored = 0
            ORDER BY favorite DESC, name COLLATE NOCASE ASC""")
        return self.cursor.fetchall()

    def toggle_readit(self, uid):
        """
        Toggle the read_it status on the post
        Returns the success of the toggle
        """
        # Find status of submission
        self.cursor.execute(
            "SELECT read_it FROM submissions WHERE id = ?",
            (uid,)
        )
        post = self.cursor.fetchone()
        if not post:
            # Submission was not found
            return False

        # Toggle column
        toggle = 0 if post['read_it'] else 1
        self.cursor.execute(
            "UPDATE submissions SET read_it = ? WHERE id = ?",
            (toggle, uid)
        )

        # Return results of the update
        if self.cursor.rowcount > 0:
            return True
        else:
            return False

    def toggle_saved(self, uid):
        """
        Toggle the saved status on the submission
        Returns the success of the toggle
        """
        # Find status of submission
        self.cursor.execute(
            "SELECT saved FROM submissions WHERE id = ?",
            (uid,)
        )
        post = self.cursor.fetchone()
        if not post:
            # Submission was not found
            return False

        # Toggle column
        toggle = 0 if post['saved'] else 1
        self.cursor.execute(
            "UPDATE submissions SET saved = ? WHERE id = ?",
            (toggle, uid)
        )

        # Return results of the update
        if self.cursor.rowcount > 0:
            return True
        else:
            return False

    def toggle_loved(self, uid):
        """
        Toggle the loved status on the submission
        Returns the success of the toggle
        """
        # Find status of submission
        self.cursor.execute(
            "SELECT loved FROM submissions WHERE id = ?",
            (uid,)
        )
        post = self.cursor.fetchone()
        if not post:
            # Submission was not found
            return False

        # Toggle column
        toggle = 0 if post['loved'] else 1
        self.cursor.execute(
            "UPDATE submissions SET loved = ? WHERE id = ?",
            (toggle, uid)
        )

        # Return results of the update
        if self.cursor.rowcount > 0:
            return True
        else:
            return False

    def read_multi(self, ids):
        print(len(ids))
        print(','.join('?'*len(ids)))
        self.cursor.execute(
            "UPDATE submissions SET read_it = 1 WHERE id IN ({all})".format(
                all=','.join(['?']*len(ids))), ids
        )

        # Return results of the update
        if self.cursor.rowcount > 0:
            return True
        else:
            return False
