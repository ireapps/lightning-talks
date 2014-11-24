import unittest

from passlib.hash import bcrypt

from models import User, Session

class TestUserModel(unittest.TestCase):
    user_dict = None
    user = None

    def setUp(self):
        self.user_dict = {
            "name": "jeremy bowers",
            "email": "jeremybowers@gmail.com",
            "password": "mytestpassword"
        }

        self.user = User(self.user_dict)
        self.user.save(test=True)

    def test_create_user_with_args(self):
        self.assertEqual(self.user.name, "jeremy bowers")

    def test_create_user_with_kwargs(self):
        self.user = User(**self.user_dict)
        self.user.save(test=True)
        self.assertEqual(self.user.name, "jeremy bowers")

    def test_repr(self):
        self.assertEqual(self.user.__repr__(), "jeremy bowers")

    def test_create_id(self):
        self.assertIsNotNone(self.user.id)

    def test_create_login_hash(self):
        self.assertIsNotNone(self.user.login_hash)

    def test_removes_password(self):
        self.assertIsNone(self.user.password)

    def test_login_hash_is_bycrypt(self):
        self.assertEqual(self.user.login_hash[:4],"$2a$")

    def test_decrypted_password(self):
        self.assertTrue(bcrypt.verify(self.user_dict['password'], self.user.login_hash))

    def tearDown(self):
        pass

class TestSessionModel(unittest.TestCase):
    user_dict = None
    user = None
    session_dict = None
    session = None

    def setUp(self):
        self.user_dict = {
            "name": "jeremy bowers",
            "email": "jeremybowers@gmail.com",
            "password": "mytestpassword"
        }

        self.user = User(self.user_dict)
        self.user.save(test=True)

        self.session_dict = {
            "title": "Too Many Cooks",
            "description": """Man: It takes a lot to make a stew
                Woman: A pinch of salt and laughter, too
                M: A scoop of kids to add the spice
                W: A dash of love to make it nice, and you've got
                Both: Too many Cooks
                W: Too many Cooks
                B: Too many Cooks
                M: Too many Cooks
                B: Too many Cooks
                W: Too many Cooks
                B: Too many Cooks""",
            "user": self.user.id,
            "votes": 0,
            "users_voting_for": []
        }

        self.session = Session(self.session_dict)
        self.session.save(test=True)

    def test_create_user_with_args(self):
        self.assertEqual(self.session.title, "Too Many Cooks")

    def test_create_user_with_kwargs(self):
        self.session = Session(**self.session_dict)
        self.session.save(test=True)
        self.assertEqual(self.session.title, "Too Many Cooks")

    def test_cast_a_vote(self):
        self.session.cast_vote(self.user.id)
        self.assertEqual(self.session.votes, 1)
        self.assertEqual(len(self.session.users_voting_for), 1)

    def test_cast_two_votes(self):
        self.session.cast_vote(self.user.id)

        user_dict = {
            "name": "heremy powers",
            "email": "haremypowers@goomail.cram",
            "password": "atestpasswordofcourse"
        }

        user = User(self.user_dict)
        user.save(test=True)

        self.session.cast_vote(user.id)

        self.assertEqual(self.session.votes, 2)
        self.assertEqual(len(self.session.users_voting_for), 2)

if __name__ == '__main__':
    unittest.main()