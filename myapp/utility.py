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