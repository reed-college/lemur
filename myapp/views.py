from flask import render_template, request, redirect, flash,url_for
from main import app

#This file contains all the views

@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

# Responses can be pretty minimal:
@app.route('/minimal')
def main():
    return "We're up!"


@app.route('/gifs/<gif>')
def gif(gif):
    return app.send_static_file('gifs/' + gif)


# Another resource; this one can take a parameter. Notice that while our first
# route responds with plain text (not even HTML), this route responds be
# rendering a template.
@app.route('/helloworld')
@app.route('/helloworld/<name>')
def hello(name=None):
    return render_template("hello.html", name=name)


# These next two routes demonstrate a "request" -- that is, the form in `form`
# will make a POST to the URL in `yousaid`, which will then unpack the request
# and respond by rendering a template.
@app.route('/form')
def form():
    return render_template("form.html")


# @app.route('/yousaid', methods=['POST'])
# def yousaid():
#     if 'bev' in request.form.keys():
#         choice = request.form['bev']
#     else:
#         choice = None
#     return render_template("bevchoice.html", bev=choice)


# # Utility method for creating all the tables in the database
# @app.route('/admin/bootstrap')
# def bootstrap():
#     schema.Base.metadata.create_all(db.engine)
#     return "Bootsrapped!"


# # This form allows us to add a new person to the database.
# @app.route('/addperson')
# def add_a_person():
#     return render_template('new_person_form.html')


# # Here is the actual method that receives our new person form.
# @app.route('/newperson', methods=['POST'])
# def add_person():
#     session = db.get_session()
#     new_person = schema.Person(
#         first_name=request.form['fname'],
#         last_name=request.form['lname']
#     )
#     session.add(new_person)
#     session.commit()

#     return 'Okay maaaade a person! {} {} has been saved'.format(
#         new_person.first_name,
#         new_person.last_name
#     )


# # This route allows us to list people from the database. With no params, we list
# # everyone; with an id resource, we list on the person who matches that id.
# @app.route('/listpeople')
# @app.route('/listpeople/<id>')
# def list_people(id=None):
#     session = db.get_session()

#     if id is None:
#         people = session.query(schema.Person).all()
#     else:
#         people = session.query(schema.Person).filter(schema.Person.id == id)
#     return render_template("person.tpl", people=people)


# if __name__ == '__main__':
#     app.run()
