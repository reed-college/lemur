
var numoOfExperiment = 1;

$(document).ready(function(){
    $('button[name=submit]').click(function(){         
        //errMsgs is a list of error messages caused by the unusual data
        //entered by students
        //feedback is the message given back to the student considering the
        //data entered
        var errMsgs = [];
        var feedback = '';
        CollectAndCheckStudentInput(errMsgs, feedback);
        if (errMsgs.length == 0){
            feedback = '<b>Congratulation! You input data looks great!</b><br>';
        }
        else{
            feedback = '<b>Your input data has the following problem(s)</b>:<br>';
            for (var i = 0; i < errMsgs.length; i++){
                feedback += ((i+1)+'.&nbsp;\t'+errMsgs[i]+'<br>');
            }
        }
        feedback += '<b>Clcik confirm to submit or go back to change your input.</b>';
        $('#errorMsgs').html(feedback);

    });

    $('button[name=confirm]').click(function(){
        dataArr2D = CollectStudentInput();
        //Communicate the lab data with python via Ajax 
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: '/_student_receive_data',
          data: JSON.stringify({'observationsGroupByStudent':dataArr2D}),
          success: function(result){
                    console.log('submit successfully!');
                },
          error : function(result){
                    errorReport('submit', result);
                }
        });
        //Redirect to the enter data page
        window.location.replace('/student_select_lab');
    });

    //Add a new column of entry
    $('button[name=newDataEntry]').click(function(){
        //The number of experiments besides student name
        var remainingExperiments = document.getElementsByClassName('customizedExperiments');
        numoOfExperiment += 1;
        $('tr[name=title]').append('<th>Data entry'+numoOfExperiment.toString()+'</th>');
        $('tr[name=studentName]').append('<td><input class=studentName name=studentName'+numoOfExperiment.toString()+'></input> </td> ');
        for (var i=0;i<remainingExperiments.length;i++){
            $(remainingExperiments[i]).append('<td><input class=studentObservation required></input> </td>');
        }
        
    });
});
