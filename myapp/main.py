from flask import (Flask, render_template, request, redirect, url_for,
                   jsonify, make_response)
import db
import schema
import ast
try:
    import simplejson as json
except (ImportError):
    import json
from utility import Generate_lab_id, Generate_row_id, Generate_data_id
# Initialize an app
app = Flask(__name__)
app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


# 1.Commands
# Utility method for creating all the tables in the database
@app.route('/admin/bootstrap')
def bootstrap():
    schema.Base.metadata.create_all(db.engine)
    return "Bootsrapped!"


# Clean all the rows in Lab_rows and Lab_desc
@app.route('/clean_database', methods=['GET'])
def clean_database():
    db_session = db.get_session()
    for r in db_session.query(schema.Lab_rows):
        db_session.delete(r)
    for d in db_session.query(schema.Lab_desc):
        db_session.delete(d)
    db_session.commit()
    return "Database has been cleaned"


# 2.Common Side
# common homepage(temporary)
@app.route('/')
def main():
    return render_template('common_home.html')


# 3.Student Side
# student homepage
@app.route('/student_home')
def student_home():
    return render_template('student_home.html')


# A student can select among all current available labs
@app.route('/student_enter_data')
def student_enter_data():
    lab_list = []
    db_session = db.get_session()
    query_all_lab = db_session.query(schema.Lab_info).all()
    for lab in query_all_lab:
        lab_list.append({'lab_name': lab.lab_name,
                         'class_name': lab.class_name,
                         'prof_name': lab.prof_name})
    return render_template('student_enter_data.html',
                           lab_list=lab_list)


# A student can input data here
@app.route('/student_data_entry/<lab_id>')
def student_data_entry(lab_id):
    rows_info = []
    lab_info = []
    db_session = db.get_session()
    query_lab_info = db_session.query(schema.Lab_info).filter(
        schema.Lab_info.lab_id == lab_id)
    query_rows_info = db_session.query(schema.Lab_rows).filter(
        schema.Lab_rows.lab_id == lab_id).order_by(schema.Lab_rows.row_order)

    # Convert the objects to dictionaries to make them JSON serializable
    for row in query_rows_info:
        rows_info.append({'row_name': row.row_name, 'row_desc': row.row_desc,
                          'value_type': row.value_type,
                          'value_range': row.value_range,
                          'value_candidates': row.value_candidates})
    for lab in query_lab_info:
        lab_info.append({'lab_id': lab.lab_id,
                         'lab_name': lab.lab_name,
                         'lab_desc': lab.lab_desc})
    return render_template('student_data_entry.html',
                           rows_info=rows_info, lab_info=lab_info)


# store incoming data into the database
@app.route('/_student_receive_data', methods=['POST'])
def _student_receive_data():
    jsonData = request.get_json()
    lab_data = jsonData['lab_data']
    db_session = db.get_session()
    for d in lab_data:
        student_name = d['student_name']
        for r in d['rows_info']:
            lab_id = r['lab_id']
            row_name = r['row_name']
            row_id = Generate_row_id(lab_id, row_name)
            data_id = Generate_data_id(row_id, student_name)
            db_session.add(schema.Lab_data(row_id=row_id, data_id=data_id,
                                           student_name=student_name,
                                           row_data=r['row_data']))
    db_session.commit()
    # return success to the ajax call from flask
    return jsonify(success=True, data=jsonData)


# 4.Admin Side
# admin homepage
@app.route('/admin_home')
def admin_home():
    return render_template('admin_home.html')


# create a new lab/manage current labs
@app.route('/admin_setup_labs_and_data_access', methods=['GET', 'POST'])
def admin_setup_labs_and_data_access():
    # Collect Info of all the existing labs
    current_labs = {'activated': [], 'downloaded': [], 'unactivated': []}
    current_labs['activated']
    current_labs['downloaded']
    current_labs['unactivated']

    db_session = db.get_session()
    query_activated = db_session.query(schema.Lab_info).filter(
        schema.Lab_info.lab_status == 'Activated')
    query_downloaded = db_session.query(schema.Lab_info).filter(
        schema.Lab_info.lab_status == 'Downloaded')
    query_unactivated = db_session.query(schema.Lab_info).filter(
        schema.Lab_info.lab_status == 'Unactivated')

    for lab_a in query_activated:
        current_labs['activated'].append({'lab_id': lab_a.lab_id,
                                          'lab_name': lab_a.lab_name,
                                          'class_name': lab_a.class_name,
                                          'prof_name': lab_a.prof_name})
    for lab_d in query_downloaded:
        current_labs['downloaded'].append({'lab_id': lab_d.lab_id,
                                           'lab_name': lab_d.lab_name,
                                           'class_name': lab_d.class_name,
                                           'prof_name': lab_d.prof_name})
    for lab_u in query_unactivated:
        current_labs['unactivated'].append({'lab_id': lab_u.lab_id,
                                            'lab_name': lab_u.lab_name,
                                            'class_name': lab_u.class_name,
                                            'prof_name': lab_u.prof_name})

    if request.method == 'POST':
        labinfo = {'lab_name': request.form['lab_name'],
                   'class_name': request.form['class_name'],
                   'prof_name': request.form['prof_name'],
                   'lab_desc': request.form['lab_desc'],
                   'lab_questions': request.form['lab_questions']}
        return redirect(url_for('.admin_setup_labs', labinfo=labinfo))
    return render_template('admin_setup_labs_and_data_access.html',
                           current_labs=current_labs)


# fill in the row details of a lab
@app.route('/admin_setup_labs')
def admin_setup_labs():
    labinfo = ast.literal_eval(request.args['labinfo'])
    return render_template('admin_setup_labs.html', labinfo=labinfo)


@app.route('/_admin_receive_setup_labs_data', methods=['POST'])
def _admin_receive_setup_labs_data():
    jsonData = request.get_json()
    lab_name = jsonData['lab_name']
    class_name = jsonData['class_name']
    prof_name = jsonData['prof_name']
    lab_desc = jsonData['lab_desc']
    row_data = jsonData['row_data']

    lab_id = Generate_lab_id(lab_name, class_name, prof_name)

    db_session = db.get_session()

    lab_rows = []
    lab = schema.Lab_info(lab_id=lab_id, lab_name=lab_name,
                          class_name=class_name, prof_name=prof_name,
                          lab_desc=lab_desc, lab_status='Activated')
    for r in row_data:
        row_name = r['row_name']
        row_id = Generate_row_id(lab_id, row_name)
        lab_rows.append(
            schema.Lab_rows(lab_id=lab_id, row_id=row_id,
                            row_name=row_name,
                            row_desc=r['row_desc'],
                            row_order=r['row_order'],
                            value_type=r['value_type'],
                            value_range=r['value_range'],
                            value_candidates=r['value_candidates']))
    lab.lab_rows = lab_rows
    db_session.add(lab)
    db_session.commit()
    # return success to the ajax call from flask
    return jsonify(success=True, data=jsonData)


# modify a current lab
@app.route('/admin_modify_lab/<lab_id>')
def admin_modify_lab(lab_id):
    db_session = db.get_session()
    # Collect the info of the current lab and send them to the template
    rows_info = []
    query_rows_of_lab_to_be_modified = db_session.query(
        schema.Lab_rows).filter(schema.Lab_rows.lab_id == lab_id)
    query_info_of_lab_to_be_modified = db_session.query(
        schema.Lab_info).filter(schema.Lab_info.lab_id == lab_id)
    for r in query_rows_of_lab_to_be_modified:
        rows_info.append({'row_name': r.row_name,
                          'row_desc': r.row_desc,
                          'row_order': r.row_order,
                          'value_type': r.value_type,
                          'value_range': r.value_range,
                          'value_candidates': r.value_candidates})
    for r in query_info_of_lab_to_be_modified:
        lab_id = r.lab_id
        lab_name = r.lab_name
        class_name = r.class_name
        prof_name = r.prof_name
        lab_desc = r.lab_desc
    # Sort the list of rows according to row_order
    sorted(rows_info, key=lambda row: row['row_order'])

    labinfo = {'lab_id': lab_id, 'lab_name': lab_name,
               'class_name': class_name,
               'prof_name': prof_name, 'lab_desc': lab_desc,
               'rows_info': rows_info}
    return render_template('admin_modify_lab.html', labinfo=labinfo)


# Delete the old lab and add the new lab
@app.route('/_admin_modify_lab', methods=['POST'])
def _admin_modify_lab():
    jsonData = request.get_json()
    lab_name = jsonData['lab_name']
    class_name = jsonData['class_name']
    prof_name = jsonData['prof_name']
    lab_desc = jsonData['lab_desc']
    row_data = jsonData['row_data']

    new_lab_id = Generate_lab_id(lab_name, class_name, prof_name)
    old_lab_id = jsonData['old_lab_id']

    db_session = db.get_session()
    query_info_to_be_deleted = db_session.query(schema.Lab_info).filter(
        schema.Lab_info.lab_id == old_lab_id)
    query_rows_to_be_deleted = db_session.query(schema.Lab_rows).filter(
        schema.Lab_rows.lab_id == old_lab_id)

    for r in query_info_to_be_deleted:
        db_session.delete(r)
    for r in query_rows_to_be_deleted:
        db_session.delete(r)

    for r in row_data:
        row_name = r['row_name']
        row_id = Generate_row_id(new_lab_id, row_name)
        db_session.add(schema.Lab_rows(lab_id=new_lab_id,
                                       row_id=row_id, row_name=row_name,
                                       row_desc=r['row_desc'],
                                       row_order=r['row_order'],
                                       value_type=r['value_type'],
                                       value_range=r['value_range'],
                                       value_candidates=r['value_candidates']))
    db_session.add(schema.Lab_info(lab_id=new_lab_id, lab_name=lab_name,
                                   class_name=class_name, prof_name=prof_name,
                                   lab_desc=lab_desc, lab_status='Activated'))

    db_session.commit()
    # return success to the ajax call from flask
    return jsonify(success=True, data=jsonData)


@app.route('/_admin_duplicate_lab', methods=['POST'])
def _admin_duplicate_lab():
    jsonData = request.get_json()
    old_lab_id = jsonData['lab_id']
    db_session = db.get_session()

    # Test the existence of the copies of this lab
    i = 1
    while True:
        copy_existence = db_session.query(schema.Lab_info).filter(
            schema.Lab_info.lab_id == 'copy'+str(i)+'_'+old_lab_id).count()
        if copy_existence == 0:
            new_lab_id = 'copy'+str(i)+'_'+old_lab_id

            query_rows_to_be_duplicated = db_session.query(
                schema.Lab_rows).filter(schema.Lab_rows.lab_id == old_lab_id)


            old_lab = db_session.query(schema.Lab_info).filter(
                schema.Lab_info.lab_id == old_lab_id).one()

            new_lab = schema.Lab_info(
                lab_id=new_lab_id, lab_name='copy'+str(i)+'_'+old_lab.lab_name,
                class_name=old_lab.class_name, prof_name=old_lab.prof_name,
                lab_desc=old_lab.lab_desc, lab_status=old_lab.lab_status)

            new_lab_rows = []
            for r in old_lab.lab_rows:
                row_name = r.row_name
                row_id = Generate_row_id(new_lab_id, row_name)
                new_lab_rows.append(schema.Lab_rows(
                    lab_id=new_lab_id, row_id=row_id, row_name=row_name,
                    row_desc=r.row_desc, row_order=r.row_order,
                    value_type=r.value_type, value_range=r.value_range,
                    value_candidates=r.value_candidates))

            new_lab.lab_rows = new_lab_rows
            db_session.add(new_lab)
            db_session.commit()
            break
        i += 1
    # return success to the ajax call from flask
    return jsonify(success=True, data=jsonData)


@app.route('/_admin_delete_lab', methods=['POST'])
def _admin_delete_lab():
    jsonData = request.get_json()
    lab_id = jsonData['lab_id']
    db_session = db.get_session()

    query_info_to_be_deleted = db_session.query(schema.Lab_info).filter(
        schema.Lab_info.lab_id == lab_id)
    query_rows_to_be_deleted = db_session.query(schema.Lab_rows).filter(
        schema.Lab_rows.lab_id == lab_id)

    for r in query_info_to_be_deleted:
        db_session.delete(r)
    for r in query_rows_to_be_deleted:
        db_session.delete(r)
    db_session.commit()

    # return success to the ajax call from flask
    return jsonify(success=True, data=jsonData)


# change the status of a lab
@app.route('/_admin_change_status/<new_status>', methods=['POST'])
def _admin_status_make_download_only(new_status):
    jsonData = request.get_json()
    lab_id = jsonData['lab_id']
    db_session = db.get_session()
    # Test the existence of the copies of this lab
    query_status_to_be_changed = db_session.query(schema.Lab_info).filter(
        schema.Lab_rows.lab_id == lab_id)

    for r in query_status_to_be_changed:
        r.lab_status = new_status
    db_session.commit()

    # return success to the ajax call from flask
    return jsonify(success=True, data=jsonData)


# select labs to review/edit data
@app.route('/admin_select_lab_for_data')
def admin_select_lab_for_data():
    lab_list = []
    db_session = db.get_session()
    for lab in db_session.query(schema.Lab_info).all():
        data_num = 0
        query_rows = db_session.query(schema.Lab_rows).filter(
            schema.Lab_rows.lab_id == lab.lab_id)
        for r in query_rows:
            data_num += db_session.query(schema.Lab_data).filter(
                schema.Lab_data.row_id == r.row_id).count()
        lab_list.append({'lab_id': lab.lab_id, 'lab_name': lab.lab_name,
                         'class_name': lab.class_name,
                         'prof_name': lab.prof_name, 'data_num': data_num})
    return render_template('admin_select_lab_for_data.html', lab_list=lab_list)


# review/edit Data
@app.route('/admin_edit_data/<lab_ids>')
def admin_edit_data(lab_ids):
    # Get a list of lab_ids that are needed to be retrieved
    lab_ids = ast.literal_eval(lab_ids)

    lab_data = []
    lab_data_by_student = []
    row_names_list = []
    err_msg = ''

    db_session = db.get_session()

    # Group row data according to row_name
    query_rows = db_session.query(schema.Lab_rows).filter(
        schema.Lab_rows.lab_id == lab_ids[0]).order_by(
        schema.Lab_rows.row_order)
    for r in query_rows:
        lab_data.append({'row_name': r.row_name, 'row_data_list': []})
        row_names_list.append(r.row_name)

    for lab_id in lab_ids:
        query_rows = db_session.query(schema.Lab_rows).filter(
            schema.Lab_rows.lab_id == lab_id).order_by(
            schema.Lab_rows.row_order)
        index = 0

        # Check whether these labs are compatitble with each other(the number
        # of rows and the names of rows must be the same)
        if query_rows.count() != len(row_names_list):
            err_msg = lab_ids[0]+' and '+lab_id+' are incompatible: the number of rows is different-'+str(query_rows.count())+' and '+str(len(row_names_list))
        else:
            for r in query_rows:
                if (row_names_list[index] != r.row_name):
                    err_msg = lab_ids[0]+' and '+lab_id+' are incompatible:'+row_names_list[index]+' and '+r.row_name+' are different row names'
                    break
                else:
                    query_datas = db_session.query(schema.Lab_data).filter(
                        schema.Lab_data.row_id == r.row_id).order_by(
                        schema.Lab_data.data_id)
                    for data in query_datas:
                        lab_data[index]['row_data_list'].append({
                            'lab_id': lab_id,
                            'student_name': data.student_name,
                            'row_id': data.row_id,
                            'data_id': data.data_id,
                            'row_data': data.row_data})

                index += 1
        if err_msg != '':
            return render_template('admin_edit_data.html',
                                   lab_data=lab_data,
                                   student_data=lab_data_by_student,
                                   b_ids=lab_ids, err_msg=err_msg)

    # Group row data according to student_name
    for row in lab_data:
        # sort row_data_list to make all the data across different lists
        sorted(row['row_data_list'], key=lambda element: element['data_id'])
        # if list is empty, add student names into it
        if not lab_data_by_student:
            for data in row['row_data_list']:
                lab_data_by_student.append({
                    'student_name': data['student_name'],
                    'lab_id': data['lab_id'], 'row_data_list': []})

        for i in range(len(row['row_data_list'])):
            data = row['row_data_list'][i]
            lab_data_by_student[i]['row_data_list'].append({
                'row_name': row['row_name'],
                'row_id': data['row_id'],
                'data_id': data['data_id'],
                'row_data': data['row_data']})
    return render_template('admin_edit_data.html',
                           lab_data=lab_data,
                           student_data=lab_data_by_student,
                           lab_ids=lab_ids,
                           err_msg=err_msg)


# change data(backend)
@app.route('/_admin_change_data', methods=['POST'])
def _admin_change_data():
    jsonData = request.get_json()
    old_data_ids_list = jsonData['old_data_ids_list']
    new_data_list = jsonData['new_data_list']
    db_session = db.get_session()
    # delete all the old data by old data_id
    for data_id in old_data_ids_list:
        query_data = db_session.query(schema.Lab_data).filter(
            schema.Lab_data.data_id == data_id)
        for r in query_data:
            db_session.delete(r)

    # add all the new data
    for d in new_data_list:
        print(schema.Lab_data(data_id=d['data_id'],
                              student_name=d['student_name'],
                              row_data=d['row_data']))
        db_session.add(schema.Lab_data(row_id=d['row_id'],
                                       data_id=d['data_id'],
                                       student_name=d['student_name'],
                                       row_data=d['row_data']))

    db_session.commit()
    # return success to the ajax call from flask
    return jsonify(success=True, data=jsonData)


# delete data(backend)
@app.route('/_admin_delete_data', methods=['POST'])
def _admin_delete_data():
    jsonData = request.get_json()
    data_ids_to_be_removed = jsonData['data_ids_to_be_removed']
    db_session = db.get_session()
    for data_id in data_ids_to_be_removed:
        query_data = db_session.query(schema.Lab_data).filter(
            schema.Lab_data.data_id == data_id)
        for r in query_data:
            db_session.delete(r)
    db_session.commit()
    # return success to the ajax call from flask
    return jsonify(success=True, data=jsonData)


# format and download data
@app.route('/_admin_download_data/<lab_ids>')
def _admin_download_data(lab_ids):
    lab_ids = ast.literal_eval(lab_ids)
    lab_data = []
    lab_data_by_student = []
    row_names_list = ['Student Name', 'Lab ID']

    db_session = db.get_session()

    # Group row data according to row_name
    query_rows = db_session.query(schema.Lab_rows).filter(
        schema.Lab_rows.lab_id == lab_ids[0]).order_by(
        schema.Lab_rows.row_order)
    for r in query_rows:
        lab_data.append({'row_name': r.row_name, 'row_data_list': []})
        row_names_list.append(r.row_name)

    for lab_id in lab_ids:
        query_rows = db_session.query(schema.Lab_rows).filter(
            schema.Lab_rows.lab_id == lab_id).order_by(
            schema.Lab_rows.row_order)
        index = 0
        for r in query_rows:
            query_datas = db_session.query(schema.Lab_data).filter(
                schema.Lab_data.row_id == r.row_id).order_by(
                schema.Lab_data.data_id)
            for data in query_datas:
                lab_data[index]['row_data_list'].append({
                    'lab_id': lab_id, 'student_name': data.student_name,
                    'data_id': data.data_id, 'row_data': data.row_data})
            index += 1

    # Group row data according to student_name
    for row in lab_data:
        # sort row_data_list to make all the data across different lists
        sorted(row['row_data_list'], key=lambda element: element['data_id'])
        # if list is empty, add student names into it
        if not lab_data_by_student:
            for data in row['row_data_list']:
                lab_data_by_student.append({
                    'student_name': data['student_name'],
                    'lab_id': data['lab_id'], 'row_data_list': []})

        for i in range(len(row['row_data_list'])):
            data = row['row_data_list'][i]
            lab_data_by_student[i]['row_data_list'].append({
                'row_name': row['row_name'], 'data_id': data['data_id'],
                'row_data': data['row_data']})

    # Format the string csv to be downloaded
    dt = '\t\t'
    nl = '\n'
    csv = dt.join(row_names_list)+nl
    for student in lab_data_by_student:
        csv += (student['student_name']+dt+student['lab_id'])
        for data in student['row_data_list']:
            csv += (dt+data['row_data'])
        csv += nl
    lab_ids_str = '+'.join(lab_ids)
    response = make_response(csv)  # create a response out of the CSV string
    response.headers["Content-Disposition"] = 'attachment; filename='+lab_ids_str+'.txt'
    # Set the right header for the response to be downloaded
    return response


# create/manage users
@app.route('/admin_manage_users', methods=['GET', 'POST'])
def admin_manage_users():
    return render_template('admin_manage_users.html')


# log out
@app.route('/admin_log_out', methods=['GET', 'POST'])
def admin_log_out():
    return render_template('admin_log_out.html')


if __name__ == '__main__':
    app.run()
