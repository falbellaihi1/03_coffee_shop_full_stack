import os
from flask import Flask, request, jsonify, abort
from pip._vendor import requests
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, create_db
from .auth.auth import AuthError, requires_auth
from functools import wraps


def create_app(test_config=None):  # create app
    app = Flask(__name__)
    setup_db(app)
    # CORS(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    '''
    @TODO uncomment the following line to initialize the datbase
    !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
    '''
    db_drop_and_create_all()
    #create_db()
    @app.after_request
    def after_request(response):  # after request header decorators
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response



    ## ROUTES

    ####################################
    '''
    @TODO implement endpoint     'DONE'
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''


    @app.route('/drinks', methods=['GET'])
    def get_drinks():  # public get drink, requires no permission, it retrieves all drinks in short format

        try:
            drinks = Drink.query.all()
            short_drinks = []
            if drinks:
                short_drinks = [drink.short() for drink in drinks]
            else:
                short_drinks = []
            return jsonify({"success": True, "drinks": short_drinks})
        except:
            abort(404)

    '''
    @TODO implement endpoint      'DONE'
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''

    @app.route('/drinks-detail',
               methods=['GET'])  # retrieves drinks in detail, it required get:drink-detail permission to return long drinks
    @requires_auth('get:drinks-detail')
    def detail_drinks(playload):
        try:

            drinks = Drink.query.all()
            if drinks:
                long_drinks = [drink.long() for drink in drinks]
            else:
                long_drinks = []
            return jsonify({"success": True, "drinks": long_drinks})
        except:
            abort(401)

    '''
    @TODO implement endpoint      'DONE'
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''

    @app.route('/drinks', methods=['POST'])
    @requires_auth('post:drinks')
    def add_drinks(
            payload):  # adds new drink requiring permission post:drinks to create it,  it gets json data and insert it into database by creating new drink
        try:
            body = request.get_json()
            title = body.get("title")
            recipe = json.dumps(body.get("recipe"))
            new_drink = Drink(title=title, recipe=recipe)
            Drink.insert(new_drink)
            drink = Drink.query.filter(Drink.id == new_drink.id).one_or_none()
            return jsonify({"success": True, "drinks": [drink.long()]})
        except:
            abort(401)

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

    @app.route('/drinks/<int:id>', methods=['PATCH'])
    @requires_auth('patch:drinks')
    def edit_drink(payload, id):
        # takes id to retrieve drink and gets json data to update the specified drink and returns it
        try:

            drink = Drink.query.filter(Drink.id == id).one_or_none()
            if not drink:
                abort(404)
            body = request.get_json()
            title = body.get("title")
            drink.title = title
            recipe = json.dumps(body.get("recipe"))
            drink.recipe = recipe
            Drink.update(drink)
            drink = Drink.query.filter_by(id=id).one_or_none()
            return jsonify({"success": True, "drinks": [drink.long()]})
        except:
            abort(401)

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

    @app.route('/drinks/<int:id>', methods=['DELETE'])
    @requires_auth('delete:drinks')
    def delete_drink(playload, id):
        # deletes drink, and returns deleted drink id, if it could not find drinkk it returns 404

        try:
            drink = Drink.query.filter(Drink.id == id).one_or_none()

            if not drink:
                abort(404)
            if (request.method == 'DELETE'):
                drink.delete()
            return jsonify({
                "success": True,
                "deleted": id,
            })
        except:
            abort(401)

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

    @app.errorhandler(401)
    def authorization(error):
        return jsonify({
            "success": False,
            "error": 401,
            "message": "you do not have the permissions to do this action"
        }), 401

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422
    '''
    @TODO implement error handler for 404
        error handler should conform to general task above 
    '''
    '''
    @TODO implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                 jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "resource not found"
                        }), 404

    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404


    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500





    '''
    @TODO implement error handler for AuthError
        error handler should conform to general task above 
    '''

    @app.errorhandler(AuthError)
    def auth_error(error): # handle auth errors and returns it as json
        print('tb')
        print(error.status_code)
        print(error.error)
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error

        }), error.status_code

    return app


if __name__ == "__main__":
    create_app().run()
