import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate(request, data):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    normalisedData = [el.format() for el in data]
    transformedData = normalisedData[start:end]
    return transformedData


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorisation')
    response.headers.add('Access-Control-Allow-Headers','GET, POST, PUT, DELETE, OPTIONS')
    return response

  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()

    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    })

  @app.route('/questions')
  def get_data():
    questions = Question.query.order_by(Question.id).all()

    formatedQuestion = paginate(request, questions)
    categories = Category.query.all()

    return jsonify({
      'success': True,
      'questions': formatedQuestion,
      'categories': {category.id: category.type for category in categories},
      'numberOfQuestions': len(questions)
    })

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question_by_id(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
      return jsonify({
        'success': True,
        'question': question.question
      })
    except:
      abort(422)

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    formData = Question(
      question = body.get('question'),
      answer = body.get('answer'),
      difficulty = body.get('difficulty'),
      category = body.get('category'),
    )
    err = False
    try:
      formData.insert()
    except:
      err = True
      abort(422)
    finally:
      if not err:
        return jsonify({
          'success': True,
        })
      else:
        print("Something Went Wrong")

  @app.route('/questions/search',methods=['POST'])
  def search():
    body = request.get_json()
    data = body.get('searchTerm', None)

    if data:
      searchData = Question.query.filter(Question.question.ilike(f'%{data}%')).all()

      return jsonify({
        'success': True,
        'questions': [el.format() for el in searchData],
      })


  @app.route('/categories/<int:category_id>/questions')
  def get_question_by_category(category_id):
    normalisedQuestion = Question.query.filter(Question.category == str(category_id))
    tranformedQuestion = [question.format() for question in normalisedQuestion]
    return jsonify({
      'success':True,
      'questions': tranformedQuestion,
    })

  @app.route('/quizzes',methods=['POST'])
  def play_quiz():
    body = request.get_json()
    category = body.get('quiz_category')
    prevQuestion = body.get('previous_questions')

    if category['id'] == 0:
      questions = Question.query.filter(Question.id.notin_(prevQuestion)).all()
    else:
      questions = Question.query.filter(Question.category == category['id']).filter(Question.id.notin_(prevQuestion)).all()

    randomisedQuestions = random.choice(questions).format()    

    return jsonify({
      'success': True,
      'question': randomisedQuestions
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  
  return app

    