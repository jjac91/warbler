import os
from unittest import TestCase
from models import db, User, Message, Follows, Likes
os.environ['DATABASE_URL'] = "postgresql:///warbler_test"
from app import app
db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        tu1=User.signup("tester1","tester1@test.com","password",None)
        user_id_1=111
        tu1.id=user_id_1
        self.uid1=user_id_1

        tu2=User.signup("tester2","tester2@test.com","password",None)
        user_id_2=222
        tu2.id=user_id_2
        self.uid2=user_id_2

        db.session.commit()
        

        self.client = app.test_client()
    
    def test_message_model(self):
        """Does basic model work?"""

        test_message = Message(
            text="test",
            user_id=self.uid1,
        )

        db.session.add(test_message)
        db.session.commit()
        test_user=User.query.get(self.uid1)
        self.assertEqual(1,len(test_user.messages))
        self.assertEqual("test", test_user.messages[0].text)
    
    def test_message_likes(self):
        """Do Likes work correctly?"""

        test_message = Message(
            text="test_like",
            user_id=self.uid1,
        )
        db.session.add(test_message)
        db.session.commit()
        test_user2=User.query.get(self.uid2)

        test_user2.likes.append(test_message)
        db.session.commit()
        self.assertEqual(1,len(test_user2.likes))
        self.assertEqual(test_user2.likes[0].id,test_message.id)
