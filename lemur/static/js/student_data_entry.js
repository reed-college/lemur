function Observation(labId,experimentName,observation) {
    this.labId = labId;
    this.experimentName = experimentName;
    this.observation = observation;
} 
var numoOfExperiment = 1;
$(document).ready(function(){
        $('button[name=submit]').click(function(){  
        
        //emptyEntry checks whether there is any empty entry left
        //wrongInput checks whether all the input are valid
        //errMsgs is a list of error messages caused by the unusual data
        //entered by students
        //feedback is the message given back to the student considering the
        //data entered
        var emptyEntry = false;
        var wrongInput = false;
        var errMsgs = [];
        var feedback = '';
        //Pack data into a 2D array
        var studentName = document.getElementsByClassName('studentName');
        for (var j=0; j<numoOfExperiment; j++){
            var currentStudentName = $(studentName[j]).val();
            var dataArr = [];
            var studentObservation = document.getElementsByClassName('studentObservation');
            //Check if the studentName is empty
            if (currentStudentName==''){
                var errMsg = 'Student Name in data entry'+numoOfExperiment.toString()+' should not be empty';
                errMsgs.push(errMsg);
            }
            
            //Find all the customized rows of the current entry
            for (var i = j; i < studentObservation.length; i+=numoOfExperiment) {
                    //a.Since the lab_name should be the same across all the entries, we 
                    //pick their values of the first entry's
                    //b.elements of different entries on the same row should have the same experimentName
                    var labId = $('form').attr('id');
                    var experimentName = $(studentObservation[i]).closest('tr').data('experimentname');
                    var observation = $(studentObservation[i]).val(); 
                    var valueType = $(studentObservation[i]).closest('tr').data('valuetype');
                    var valueRange = $(studentObservation[i]).closest('tr').data('valuerange');
                    var valueCandidates =$(studentObservation[i]).closest('tr').data('valuecandidates');
                    if (observation==''){
                        emptyEntry = true;
                        var errMsg = experimentName+' in data entry'+numoOfExperiment.toString()+' should not be empty';
                        errMsgs.push(errMsg);
                    }
                    //validate the input data
                    result = checkInputStudent(observation,valueType,valueRange,valueCandidates);
                    if (result.wrongInput){
                        wrongInput = true;
                        errMsgs.push(result.errMsg);
                    } 
            }
        }

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
        //Pack data into a 2D array
        dataArr2D = [];
        var studentName = document.getElementsByClassName('studentName');
        for (var j=0; j<numoOfExperiment; j++){
            var currentStudentName = $(studentName[j]).val();
            var dataArr = [];
            var studentObservation = document.getElementsByClassName('studentObservation');
            //Find all the customized rows of the current entry
            for (var i = j; i < studentObservation.length; i+=numoOfExperiment) {
                    //a.Since the lab_name should be the same across all the entries, we 
                    //pick their values of the first entry's
                    //b.elements of different entries on the same row should have the same experimentName
                    var labId = $('form').attr('id');
                    var experimentName = $(studentObservation[i]).closest('tr').data('experimentname');
                    var observation = $(studentObservation[i]).val(); 
                    var valueType = $(studentObservation[i]).closest('tr').data('valuetype');
                    var valueRange = $(studentObservation[i]).closest('tr').data('valuerange');
                    var valueCandidates =$(studentObservation[i]).closest('tr').data('valuecandidates');
                    
                    newObservation = new Observation(labId,experimentName,observation);
                    dataArr.push(newObservation);
            }
            dataArr2D.push({'studentName':currentStudentName,'observationsForOneExperiment':dataArr});
        }
        //Communicate the lab data with python via Ajax 
        console.log(dataArr2D);
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: 'http://127.0.0.1:5000/_student_receive_data',
          data: JSON.stringify({'observationsGroupByStudent':dataArr2D}),
          success: function(result){
                  console.log('submit successfully!');
                },
          error : function(result){
                  console.log(result);
                  console.log('fail to submit');
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
