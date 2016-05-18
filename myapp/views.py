from flask import render_template, request, redirect, flash,url_for
from main import app

#This file contains all the views

@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

