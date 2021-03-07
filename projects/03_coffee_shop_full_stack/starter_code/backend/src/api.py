import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_normaldrinks():
    err = True
    try:
        drinks = Drink.query.all()
        
        formattedDrinks = [el.short() for el in drinks]
        return jsonify({
            'success': True,
            'drinks': formattedDrinks
        })
    except Exception as error:
        err = True
        print(sys.exc_info())
        abort(404)

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_completedrinks(jwt):
    err = False
    try:
        drinks = Drink.query.order_by(id).all()
        formattedDrinks = [el.long() for el in drinks]
        return jsonify({
            'success': True,
            'drinks': formattedDrinks
        })
    except Exception as error:
        err = True
        print(sys.exc_info())
        abort(404)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):
    body = request.get_json()
    drinks = Drink(
            title=body.get('title'),
            recipe=body.get('recipe'),
        )
    try:
        if(title not in body and recipe not in body):
            err = True
            print(body)
        else:
            drinks.insert()
        
        return jsonify({
            'success': True,
            'drinks': [drinks.long()]
        })
    except Exception as error:
        err = True
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_err(e):
    return jsonify({
        'success': False,
        'status-code': e.status_code,
        'message': e.error,
    }, 401)
