import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres@{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Which city has the Eiffel Tower?',
            'answer': 'Paris', 
            'difficulty': 1, 
            'category': 3
        }

        self.bad_question = {
            'question': 'Which city has the Eiffel Tower?',
            'answer': 'Paris', 
            'difficulty': 1, 
            'category': 10
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors. Note ---> This test code is tested on a test db and not the actual application db.
    """
    #-----------------------  Test categories -----------------------#

    def test_get_categories(self):
        res = self.client.get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['categories']), 6)

    #------------------------ Test questions ------------------------#
    def test_get_questions(self):
        res = self.client.get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(data['questions'])
        # If you want to run the assertion below, comment out the test_delete_question(self) function since it deletes the entries and hence will result in one less than total number of remaining questions in the test db.

        # self.assertEqual(data['total_questions'], 18)

    def test_404_get_questions_invalid_page(self):
        res = self.client.get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'])
        self.assertEqual(data['error'], 404)

    #-------------------- Test delete question -------------------------#
    def test_delete_question(self):
        res = self.client.delete('/questions/19')
        data = json.loads(res.data)

        question = Question.query.filter_by(id=19).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted'], 19)
        self.assertEqual(data['success'],True)
        self.assertEqual(question, None)

    def test_422_question_non_existent(self):
        res = self.client.delete('/questions/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Not processable')
        self.assertEqual(data['success'], False)

    #--------------------- Test Add question --------------------------#
    def test_add_get_page(self):
        res = self.client.get('/add')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data['categories']), 6)
        self.assertTrue(data['categories'], True)

    def test_add_question(self):
        res = self.client.post('/add', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question added successfully')
    
    def test_400_add_bad_question(self):
        res = self.client.post('/add',json=self.bad_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['message'], 'Bad request')
        self.assertEqual(data['success'], False)
    
    #------------------------ Test Search ------------------------#
    def test_search_questions(self):
        res = self.client.post('/questions', json={'searchTerm':'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['totalQuestions'], True)
        self.assertTrue(data['questions'], True)
        self.assertEqual(data['success'], True)
    
    #----------------- Test questions by Category --------------------#
    def test_questions_by_category(self):
        res = self.client.get('/categories/4/questions')
        data = json.loads(res.data)

        category = Category.query.filter_by(id=4).first().format()['type']

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['totalQuestions'], True)
        self.assertTrue(data['questions'], True)
        self.assertEqual(data['currentCategory'], 'Entertainment')
    
    def test_422_no_question_of_category(self):
        res = self.client.get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Not processable')
        self.assertEqual(data['success'], False)
        
    # #---------------------- Test Quiz Page ---------------------#
    def test_quiz_page(self):
        res = self.client.post('/quizzes', json={'previous_questions':[],'quiz_category': {'type': {'id' : 5, 'type': 'Entertainment'}, 'id': 4}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'], True)
    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
