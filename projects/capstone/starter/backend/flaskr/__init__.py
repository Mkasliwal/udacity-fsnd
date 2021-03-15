import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
import json

from models import setup_db, Question, Category
from auth import AuthError, requires_auth

QUESTIONS_PER_PAGE = 10


def paginate(request, data):
    limit_rows = request.args.get('limit', QUESTIONS_PER_PAGE, type=int)
    selected_page = request.args.get('page', 1, type=int)
    current_index = selected_page - 1
    filteredData = data.limit(limit_rows).offset(
        current_index * limit_rows).all()
    transformedData = [el.format() for el in filteredData]
    return transformedData


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # @app.after_request
    # def after_request(response):
    #     response.headers.add(
    #         'Access-Control-Allow-Headers',
    #         'Content-Type, Authorisation'
    #         )
    #     response.headers.add(
    #         'Access-Control-Allow-Headers',
    #         'GET, POST, PUT, DELETE, OPTIONS'
    #         )
    #     return response

    @app.route('/categories')
    @requires_auth('get:categories')
    def get_categories(jwt):
        err = False
        try:
            categories = Category.query.all()
            if len(categories) == 0:
                err = True
        except Exception as error:
            err = True
            print('Error Occured: {}', format(error))
        finally:
            if not err:
                return jsonify({
                    'success': True,
                    'categories': {
                        category.id: category.type for category in categories
                        }
                })
            else:
                abort(404)

    @app.route('/questions')
    @requires_auth('get:questions')
    def get_data(jwt):
        err = False
        try:
            questions = Question.query.order_by(Question.id)
            formatedQuestion = paginate(request, questions)
            categories = Category.query.all()
            if len(formatedQuestion) == 0:
                err = True
        except Exception as error:
            err = True
            print(sys.exc_info())
            print('Error Occured: {}', format(error))
        finally:
            if not err:
                return jsonify({
                    'success': True,
                    'questions': formatedQuestion,
                    'categories': {
                        category.id: category.type for category in categories
                        },
                    'total_questions': len(questions.all()),
                    'currentCategory': None
                })
            else:
                abort(404)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question_by_id(question_id):
        err = False
        try:
            question = Question.query.get(question_id)
            if question:
                question.delete()
            else:
                err = True
        except Exception as error:
            err = True
            print('Error Occured: {}', format(error))
        finally:
            if not err:
                return jsonify({
                    'success': True,
                    'question': question.id
                })
            else:
                abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        formData = Question(
          question=body.get('question'),
          answer=body.get('answer'),
          difficulty=body.get('difficulty'),
          category=body.get('category'),
        )
        err = False
        try:
            if (
                'question' in body and
                'answer' in body and
                'difficulty' in body and
                'category' in body
            ):
                formData.insert()
            else:
                err = True
        except Exception as error:
            err = True
            print('Error Occured: {}', format(error))
        finally:
            if not err:
                return jsonify({
                    'success': True,
                })
            else:
                abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search():
        err = False
        try:
            body = request.get_json()
            data = body.get('searchTerm', None)
            searchData = Question.query.filter(
                Question.question.ilike(f'%{data}%')
                ).all()
            if len(searchData) == 0:
                err = True
        except Exception as error:
            err = True
            print('Error Occured: {}', format(error))
        finally:
            if not err:
                return jsonify({
                    'success': True,
                    'questions': [el.format() for el in searchData],
                })
            else:
                abort(404)

    @app.route('/categories/<int:category_id>/questions')
    def get_question_by_category(category_id):
        err = False
        try:
            normalisedQuestion = Question.query.filter(
                Question.category == str(category_id))
            tranformedQuestion = [
                question.format() for question in normalisedQuestion
                ]

            if len(tranformedQuestion) == 0:
                err = True
        except Exception as error:
            err = True
            print('Error Occured: {}', format(error))
        finally:
            if not err:
                return jsonify({
                    'success': True,
                    'questions': tranformedQuestion,
                })
            else:
                abort(404)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        err = False
        try:
            body = request.get_json()
            category = body.get('quiz_category')
            prevQuestion = body.get(
                'previous_questions'
                )

            if (
                'quiz_category' not in body and
                'previous_questions' not in body
            ):
                err = True

            if category['id'] == 0:
                questions = Question.query.filter(
                    Question.id.notin_(prevQuestion)).all()
            else:
                questions = Question.query.filter(
                    Question.category == category['id']
                    ).filter(Question.id.notin_(prevQuestion)).all()

            if len(questions) == 0:
                return jsonify({
                  'success': True
                })

            randomisedQuestions = random.choice(questions).format()

            return jsonify({
                'success': True,
                'question': randomisedQuestions
            })

        except Exception as error:
            err = True
            abort(404)
            print('Error Occured: {}', format(error))

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Page Not Found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable'
        }), 422
    return app
