import unittest

from passlib.hash import bcrypt

import fabfile
import models
import settings
import utils

class Testmodels.UserModel(unittest.TestCase):
    user_dict = None
    user = None

    def setUp(self):
        users = fabfile.load_users()
        self.user_dict = users[0]
        self.user = models.User(self.user_dict)
        self.user.save(test=True)

    def test_create_user_with_args(self):
        self.assertEqual(self.user.name, "jeremy bowers")

    def test_create_user_with_kwargs(self):
        self.user = models.User(**self.user_dict)
        self.user.save(test=True)
        self.assertEqual(self.user.name, "jeremy bowers")

    def test_repr(self):
        self.assertEqual(self.user.__repr__(), "jeremy bowers")

    def test_create_id(self):
        self.assertIsNotNone(self.user._id)

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

class Testmodels.SessionModel(unittest.TestCase):
    user_dict = None
    user = None
    session_dict = None
    session = None

    def setUp(self):
        users = fabfile.load_users()
        self.user_dict = users[0]
        self.user = models.User(self.user_dict)
        self.user.save(test=True)

        sessions = fabfile.load_sessions()
        self.session_dict = sessions[0]
        self.session = models.Session(self.session_dict)
        self.session.save(test=True)

    def test_create_user_with_args(self):
        self.assertEqual(self.session.title, "Having The Time Of Your Life")

    def test_create_user_with_kwargs(self):
        self.session = models.Session(**self.session_dict)
        self.session.save(test=True)
        self.assertEqual(self.session.title, "Having The Time Of Your Life")


if __name__ == '__main__':
    unittest.main()