"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


from multiprocessing import set_forkserver_preload
import os
from unittest import TestCase
from urllib import response

from models import Follows, db, connect_db, Message, User,Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Tests for User Views"""

    db.drop_all()
    db.create_all()

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        self.client = app.test_client()

        self.tu1=User.signup("tester1","tester1@test.com","password1",None)
        user_id_1=111
        self.tu1.id=user_id_1
        self.uid1=user_id_1

        self.tu2=User.signup("tester2","tester2@test.com","password2",None)
        user_id_2=222
        self.tu2.id=user_id_2
        self.uid2=user_id_2
        db.session.commit()
##Followers and Following
    def setUp_followers(self):
        """Sets up followers for testing"""
        follow1=Follows(user_being_followed_id=self.uid1, user_following_id=self.uid2)
        db.session.add(follow1)
        db.session.commit()
    
    def test_followers_no_authentication(self):
        """Tests ability to view the followers page without authentication"""
        self.setUp_followers()
        with self.client as client:

            response = client.get(f"/users/{self.tu1.id}/followers", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("@tester2", str(response.data))
            self.assertIn("Access unauthorized", str(response.data))
    
    def test_show_followers(self):
        """Tests ability to show followers"""
        self.setUp_followers()
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.tu1.id
            
            response = client.get(f"/users/{self.tu1.id}/followers")
            self.assertIn("@tester2",str(response.data))
            self.assertNotIn("@tester3",str(response.data))

    def test_following_no_authentication(self):
        """Tests ability to view the following page without authentication"""
        self.setUp_followers()
        with self.client as client:

            response = client.get(f"/users/{self.tu1.id}/following", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("@tester1", str(response.data))
            self.assertIn("Access unauthorized", str(response.data))
    
    def test_show_following(self):
        """Tests ability to show following"""
        self.setUp_followers()
        with self.client as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.tu2.id
            
            response = client.get(f"/users/{self.tu2.id}/following")
            self.assertIn("@tester1",str(response.data))
            self.assertNotIn("@tester3",str(response.data))
### Default views
    def test_index(self):
        """Tests user index display"""
        with self.client as client:

            resp = client.get("/users")
            self.assertIn("@tester1", str(resp.data))
            self.assertIn("@tester2", str(resp.data))
            self.assertNotIn("@tester5", str(resp.data))
    
    def test_search(self):
        """tests search function"""
        with self.client as client:
            resp = client.get("/users?q=test")

            self.assertIn("@tester1", str(resp.data))
            self.assertIn("@tester2", str(resp.data))            

            self.assertNotIn("@tester3", str(resp.data))
    
    def test_user_details(self):
        """tests user page"""
        with self.client as client:
            resp = client.get(f"/users/{self.tu1.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@tester1", str(resp.data))
###Likes

    def test_add_remove_likes(self):
        """tests adding and removing likes"""
        me1= Message(id=9999, text="This is liked", user_id=self.tu1.id)
        db.session.add(me1)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.tu2.id
            resp = client.post("/users/9999/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            
            likes = Likes.query.filter(Likes.message_id==9999).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.tu2.id)

            resp = client.post("/users/9999/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==9999).all()
            self.assertEqual(len(likes), 0)

    def test_unauthenticated_like(self):
        """tests likes without authentication"""
        me1= Message(id=9999, text="This is liked", user_id=self.tu1.id)
        db.session.add(me1)
        db.session.commit()

        like_count = Likes.query.count()

        with self.client as client:
            resp = client.post(f"/users/{me1.id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized", str(resp.data))

            self.assertEqual(like_count, Likes.query.count())

    def test_displayed_like(self):
        """tests display of likes"""
        me1= Message(id=9999, text="This is liked", user_id=self.tu1.id)
        db.session.add(me1)
        db.session.commit()
        l1 = Likes(user_id=self.tu2.id, message_id=9999)
        db.session.add(l1)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.tu2.id
            resp = client.get(f"/users/{self.tu2.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<a href="/users/222/likes">1</a>', html)


            

