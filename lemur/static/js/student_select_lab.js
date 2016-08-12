$(document).ready(function(){
    $('button[name=goToLab]').click(function(){
        var labId = '';
        var radios = document.getElementsByTagName('input')
        for (var i = 0; i < radios.length; i++) {
            if (radios[i].type == 'radio' && radios[i].checked) {
                labName = $(radios[i]).data('labname');   
                classId = $(radios[i]).data('classid');  
                className = decomposeClassId(classId)[0];
                professorName = $(radios[i]).data('profname');
                labId = generateLabId(labName,classId);
                break;
            }
        }
        if (labId==''){
            $('#errMsgNoLabChoosed').show().delay(1000).fadeOut();
        }
        else{
            window.location.replace('/student_data_entry/'+labId);
        }
    });
});
