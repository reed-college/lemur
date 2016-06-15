from flask import make_response
import db
import schema


# Utility functions
# Generate a lab's id according to lab_name, class_name and prof_name
def Generate_lab_id(lab_name,class_name,prof_name):
    return lab_name+'_'+class_name+'_'+prof_name


# Generate a row's id according to lab_id, row_name
def Generate_row_id(lab_id,row_name):
    return lab_id+':'+row_name


# Generate a data's id according to row_id, student_name
def Generate_data_id(row_id,student_name):
    return row_id+':'+student_name

# Check the existence of args in a form
def Check_existence(form, *args):
	err_msg = ''
	for a in args:
		if not(a in form):
			err_msg += 'You must send a JSON object '+a+'\n'
	return err_msg  

# Query data entered by students for lab with lab_ids
def Query_data(lab_ids):
	lab_data = []
	lab_data_by_student = []
	row_names_list = []
	err_msg = ''
	undownloadable_labs = ''
	db_session = db.get_session()
	try:        
	    # Group row data according to row_name
	    query_rows = db_session.query(schema.Lab_rows).filter(
	    	schema.Lab_rows.lab_id == lab_ids[0]).order_by(
	    	schema.Lab_rows.row_order)
	    for r in query_rows:
	    	lab_data.append({'row_name': r.row_name, 'row_data_list': []})
	    	row_names_list.append(r.row_name)
	    for lab_id in lab_ids:
	    	lab_status = db_session.query(schema.Lab_info).filter(schema.Lab_info.lab_id == lab_id).one().lab_status 
	    	if lab_status != 'Downloaded':
	    		undownloadable_labs += (str(lab_id)+'\t')

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
	except Exception as ex:
		db_session.rollback()
		template = "An exception of type {0} occured. Arguments:\n{1!r}"
		err_msg = template.format(type(ex).__name__, ex.args)
	return (lab_data, lab_data_by_student, row_names_list, err_msg, undownloadable_labs)

# Format the string csv to be downloaded
def Format_download(lab_data_by_student,row_names_list,lab_ids):

    dt = '\t\t'
    nl = '\n'
    csv = dt.join(row_names_list)+nl
    for student in lab_data_by_student:
        csv += (student['student_name']+dt+student['lab_id'])
        for data in student['row_data_list']:
            csv += (dt+data['row_data'])
        csv += nl
    lab_ids_str = '+'.join(lab_ids)
    # create a response out of the CSV string
    response = make_response(csv)  
    # Set the right header for the response to be downloaded
    response.headers["Content-Disposition"] = 'attachment; filename='+lab_ids_str+'.txt'
    return response 