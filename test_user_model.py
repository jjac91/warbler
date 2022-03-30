"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


#from cgi import test
import os
from sqlalchemy import exc
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        tu1=User.signup("tester1","tester1@test.com","password",None)
        user_id_1=111
        tu1.id=user_id_1

        tu2=User.signup("tester2","tester2@test.com","password",None)
        user_id_2=222
        tu2.id=user_id_2

        db.session.commit()
        

        self.client = app.test_client()


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_repr_(self):
        """Does __repr__ work?"""
        u = User.query.get(111)
        teststring = (repr(u))
        self.assertEqual(teststring,"<User #111: tester1, tester1@test.com>")

    #########
    #Testing following
    #########
    def test_is_following(self):
        """Does is_following work?"""
        u1 = User.query.get(111)
        u2 = User.query.get(222)

        self.assertEqual(u1.is_following(u2),False)

        u1.following.append(u2)
        db.session.commit()

        self.assertEqual(u1.is_following(u2),True)
    
    def test_is_followed_by(self):
        """Does is_followed_by work?"""
        u1 = User.query.get(111)
        u2 = User.query.get(222)

        self.assertEqual(u1.is_followed_by(u2),False)

        u2.following.append(u1)
        db.session.commit()

        self.assertEqual(u1.is_followed_by(u2),True)
    ######
    #Signup tets
    ######
    def test_valid_signup(self):
        """Does sign up work with valid values?"""
        sign_up_test_user= User.signup("tester999","test999@test.com", "tester999", None)
        user_id=999
        sign_up_test_user.id=user_id
        db.session.commit()

        tester=User.query.get(user_id)
        self.assertIsNotNone(tester)
        self.assertEqual(tester.username, "tester999")
        self.assertEqual(tester.email, "test999@test.com")
        self.assertNotEqual(tester.password, "tester999")
        self.assertTrue(tester.password.startswith("$2b$"))
    
    def test_invalid_signup_username(self):
         """Does sign up work with invalid username"""
         invalid_user= User.signup(None,"test1000@test.com", "tester1000", None)
         user_id=1000
         invalid_user.id=user_id
         with self.assertRaises(exc.InvalidRequestError) as context:
             db.session.commit()
    
    #####
    #Authentication Tests
    ####
    def test_valid_login(self):
        """Does login work with correct credentials?"""
        u1 = User.query.get(111)
        test = User.authenticate("tester1","password")
        self.assertIsNotNone(test)
        self.assertEqual(u1,test)
    
    def test_invalid_login_username(self):
        """Does login work with inccorrect username?"""
        u1 = User.query.get(111)
        test = User.authenticate("","password")
        self.assertEqual(test,False)
        self.assertNotEqual(u1,test)

    def test_invalid_password(self):
        """Does login work with inccorrect password?"""
        u1 = User.query.get(111)
        test = User.authenticate("tester1","")
        self.assertEqual(test,False)
        self.assertNotEqual(u1,test)







    
