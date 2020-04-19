import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  question_current = questions[start:end]

  return question_current

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

  @app.after_request
  def set_headers(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,authorization,True')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    data = []
    categories = Category.query.all()
    for category in categories:
      category = category.format()
      data.append(category)
    return jsonify({
      'categories' : data
    })
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
    all_questions = Question.query.all()
    format_questions = paginate_questions(request, all_questions)
    all_categories = Category.query.all()
    format_categories = [category.format() for category in all_categories]

    print('Total ques >>>> ', len(all_questions))

    if len(format_questions) == 0:
      abort(404)

    return jsonify({
      'questions': format_questions,
      'total_questions': len(all_questions),
      'categories': format_categories,
      'current_category': None,
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question_to_delete = Question.query.filter_by(id=question_id).first()
    if question_to_delete:
      question_to_delete.delete()
      return jsonify({
      'success' :True,
      'deleted' : question_id,
      })
    else:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/add', methods=['GET','POST'])
  def add_new_question():
    all_categories = Category.query.all()
    format_categories = [category.format() for category in all_categories]

    # GET request
    if request.method == 'GET':
      if len(format_categories):  
        return jsonify({
        'categories' : format_categories
        })
      else:
        abort(422) 
    
    # POST request
    if request.method == 'POST':
      question = request.get_json().get('question')
      answer = request.get_json().get('answer')
      difficulty = request.get_json().get('difficulty')
      category = request.get_json().get('category')

      if question and answer and (difficulty and 1<=difficulty<=5) and (category and 1<=category<=6):
        new_quiz_entry = Question(question=question, answer=answer,difficulty=difficulty,category=category)
        Question.insert(new_quiz_entry)
        return jsonify({
          'success' : True,
          'message' : 'Question added successfully',
        })
      else :
        abort(400)
      
    
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions', methods=['POST'])
  def search_question():
    search_query = request.get_json().get('searchTerm')
    filtered_ques = Question.query.filter(Question.question.ilike(f'%{search_query}%')).all()
    questions = [question.format() for question in filtered_ques]
    return jsonify({
      'questions' : questions,
      'totalQuestions' : len(questions),
      'currentCategory' : None,
      'success' : True
    })
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def questions_by_category(category_id):
    if 0 <= category_id < 6:
      question_category = category_id + 1
      curr_category = Category.query.filter_by(id=question_category).first().type
      questions_of_category = Question.query.filter_by(category=question_category).all()
      questions = [question.format() for question in questions_of_category]
      return jsonify({
        'questions' : questions,
        'totalQuestions' : len(questions),
        'currentCategory' : curr_category
      })
    else:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/play')
  def quiz_category():
    categories = Category.query.all()
    format_categories = [category.format() for category in categories]
    print('Play Quiz', format_categories)
    return jsonify({
      'categories' : format_categories
    })

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    previous_questions = request.get_json().get('previous_questions')
    quiz_category = request.get_json().get('quiz_category')
    all_questions = Question.query.all()
    format_all_questions = [question.format() for question in all_questions]
    quiz_question = ""

    print('Quiz category >>>> ', quiz_category)

    if quiz_category['type'] == 'click':
      for question in format_all_questions:
        question = random.choice(format_all_questions)
        if(question['id'] not in previous_questions):
          quiz_question = question
          print('Quiz question', quiz_question)
      return jsonify({
        'question' : quiz_question
      }) 
    else :
    category = quiz_category['type']['id']
    for question in format_all_questions:
        question = random.choice(format_all_questions)
        if(question['category'] == category and question['id'] not in previous_questions):
          quiz_question = question
          print('Quiz question', quiz_question)
    return jsonify({
        'question' : quiz_question
    })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request_400(error):
    return jsonify({
      'error': 400,
      'success': False,
      'message':'Bad request'
    }), 400

  @app.errorhandler(404)
  def not_found_404(error):
    return jsonify({
      'success' : False,
      'error' : 404,
      'message' : 'Page not found'
    }), 404

  @app.errorhandler(422)
  def not_processable(error):
    return jsonify({
        'error' : 422,
        'message' : 'Not processable',
        'success' : False
        }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'error' : 500,
      'message' : 'Internal server error',
      'success' : False
    })
  
  return app

    