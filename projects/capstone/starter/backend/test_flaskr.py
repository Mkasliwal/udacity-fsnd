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
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://postgres:131252118@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_successful_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])

    def test_unsuccessful_questions_get_request(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Page Not Found')

    def test_successful_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
    
    def test_unsuccessful_categories_get_request(self):
        res = self.client().get('/categories/10')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Page Not Found')

    def test_successful_questions_delete_request(self):
        question = Question(question='Test Question', answer='Test answer', difficulty=4, category=5)
        question.insert()
        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)

        question = Question.query.get(question.id)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])

    def test_unsuccessful_questions_delete_request(self):
        res = self.client().delete('/questions/50')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Unprocessable')

    def test_successful_create_question(self):
        question = {'question':'Test Question 2', 'answer':'Test answer 2', 'difficulty':3, 'category':2}
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
    
    def test_unsuccessful_questions_post_request(self):
        question = {'question':'Test Question 2', 'answer':'Test answer 2'}
        res = self.client().post('/questions', json=question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Unprocessable')

    def test_successful_search_question(self):
        searchTerm = {'searchTerm':'Test Question 2'}
        res = self.client().post('/questions/search', json=searchTerm)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])

    def test_unsuccessful_search_question(self):
        searchTerm = {'searchTerm':'15648'}
        res = self.client().post('/questions/search', json=searchTerm)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'Page Not Found')

    def test_successful_get_question_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        questions = Question.query.filter(Question.category == 2)
        transformedQuestion = [question.format() for question in questions]

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])

    def test_unsuccessful_get_question_by_category(self):
        res = self.client().get('/categories/500/questions')
        data = json.loads(res.data)
        questions = Question.query.filter(Question.category == 500)
        transformedQuestion = [question.format() for question in questions]

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'Page Not Found')

    def test_successful_quiz_play(self):
        quizQuestion = {'previous_questions': [], 'quiz_category': {'type': 'Entertainment', 'id': 1}}

        res = self.client().post('/quizzes', json=quizQuestion)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_unsuccessful_quiz_play(self):
        quizQuestion = {'quiz_category': {'type': 'Entertainment', 'id': 1000}}
        res = self.client().post('/quizzes', json=quizQuestion)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'Page Not Found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()