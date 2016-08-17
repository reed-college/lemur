// --- Functions in student_data_entry.js ---
// Check whether value is in array
function isInArray(value, array) {
    return array.indexOf(value) > -1;
}
// Check whether n is a number 
function isNumeric(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}
// Validate the input when the student enters data
function checkInputStudent(observation,valueType,valueRange,valueCandidates){
    var wrongInput = false;
    var errMsg = '';
    valueCandidates
    if (valueType == 'Text' && valueCandidates.length>0){
        valueCandidates_arr = valueCandidates.split(',');
        if (!isInArray(observation,valueCandidates_arr)){
            wrongInput = true;
            if (observation == ''){ observation = NaN;}
            errMsg = observation + ' is not in the value candidates: ' + valueCandidates; 
        }        
    }
    else if (valueType=='Number' && valueRange.length>0){
        valueRangeArray = valueRange.split('-');
        var min = parseFloat(valueRangeArray[0]);
        var max = parseFloat(valueRangeArray[1]);
        var observation = parseFloat(observation);
        if (!isNumeric(observation)){
            wrongInput = true;
            errMsg = observation + ' is not a number.';
        }
        else if (observation < min || observation > max){
            wrongInput = true;
            errMsg = observation + ' is not in the value range: ' + valueRange;
        }
    }
    return {'wrongInput':wrongInput,'errMsg':errMsg};
}

function CollectAndCheckStudentInput(errMsgs, feedback){
    //emptyEntry checks whether there is any empty entry left
    //wrongInput checks whether all the input are valid
    var emptyEntry = false;
    var wrongInput = false;
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
}

//
function CollectStudentInput(){
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
    return dataArr2D;
}

// An Observation object is used to organize inputs
function Observation(labId,experimentName,observation) {
    this.labId = labId;
    this.experimentName = experimentName;
    this.observation = observation;
} 


// --- Functions in student_select_lab.js ---
function decomposeClassId(classId){
    classInfo = classId.split('_')
    return classInfo;
}
function generateLabId(labName,classId){
    return labName+':'+classId;
}

// --- Functions in admin_edit_data.js ---
function generateObservationId(experimentId,studentName){
    return experimentId+':'+studentName;
}

// --- Functions in admin_modify_lab.js ---
// Show Value Range/Value Type field according to user's choice of value Type field
function ShowFieldByChoice(){
    var selects = document.getElementsByClassName('valueType');
    for (var i = 0; i<selects.length; i++){
        var s = selects[i];
        var selectValue = s.getElementsByClassName('selectpicker')[0].value;
        var divText =  s.getElementsByClassName('valueCandidates')[0];
        var divNumber =  s.getElementsByClassName('valueRange')[0];
        if (selectValue == 'Text') {
             divText.style.display = 'block';
             divNumber.style.display = 'none';
        }
        else {
            divText.style.display = 'none';
            divNumber.style.display = 'block';
        }  
    }
}

//Create a class to store the info of each row
function Experiment(name,description,order,valueType,valueRange,valueCandidates) {
    this.name = name;
    this.description = description;
    this.order = order;
    this.valueType = valueType;
    this.valueRange = valueRange;
    this.valueCandidates = valueCandidates;
}

// newIndexStr represents the default number/order of the newly generated question
function generateNewQuestion(newIndexStr){
    newQuestion =  '<div class="col-lg-6 col-md-6 col-sm-6 mb experiment" name="'+newIndexStr+'" id="question">'+
                       '<h4>Question'+newIndexStr+':</h4>'+
                       '<label> Name*: </label>'+
                       '<input type="text" name="experimentName" pattern="'+PATTERN_FOR_NAME+'" title="'+PATTERN_FOR_NAME_HINT+'" required>'+
                       '<br>'+
                       '<label>Description:</label>'+
                       '<br>'+
                       '<textarea class="longInput" cols="30" rows="5" name="experimentDescription" pattern="'+PATTERN_FOR_EXPERIMENT_DESCRIPTION+'" title="'+PATTERN_FOR_EXPERIMENT_DESCRIPTION_HINT+'"></textarea>'+
                       '<div class="valueType">'+
                       '<label>Value Type*: </label>'+
                       '<select class="selectpicker" data-style="btn-inverse" data-width="auto" name="valueType" title="Choose A Value Type" required>'+
                       '<option value="Text" selected="selected">Text</option>'+
                       '<option value="Number">Number</option>'+
                       '</select>'+
                       '<div class="valueRange" style="display: none;">'+
                       '<label>Value Range: </label>'+
                       '<input type="text" name="valueRange" pattern="'+PATTERN_FOR_VALUE_RANGE+'" title="'+PATTERN_FOR_VALUE_RANGE_HINT+'">'+
                       '</div>'+
                       '<div class="valueCandidates" style="display: block;">'+
                       '<label>Value Candidates: </label>'+
                       '<input type="text" name="valueCandidates" pattern="'+PATTERN_FOR_VALUE_CANDIDATES+'" title="'+PATTERN_FOR_VALUE_CANDIDATES_HINT+'">'+
                       '</div>'+
                       '</div>'+
                       '<label>Order Number: </label>'+
                       '<input type="number" name="experimentOrder"  value='+newIndexStr+' min="1" step="1" required>'+
                   '</div>';
    return newQuestion;
}

// Collect all the input for lab
function collectLabData(){
    var oldLabId = $('input[name=oldLabId]').val();
    var labName = $('input[name=labName]').val();
    var classId = $('select[name=classId]').val();
    var labDescription = $('textarea[name=labDescription]').val();
    var existingExperiments = document.getElementsByClassName('experiment');
    for (var i=0;i<existingExperiments.length;i++){
        var experimentName = $($(existingExperiments[i]).find('input[name=experimentName]')).val();
        var experimentDescription = $($(existingExperiments[i]).find('textarea[name=experimentDescription]')).val();
        var experimentOrder = $($(existingExperiments[i]).find('input[name=experimentOrder]')).val();
        var valueType = $($(existingExperiments[i]).find('select[name=valueType]')).val();
        var valueRange = $($(existingExperiments[i]).find('input[name=valueRange]')).val();
        var valueCandidates = $($(existingExperiments[i]).find('input[name=valueCandidates]')).val();
        
        newExperiment = new Experiment(experimentName,experimentDescription,experimentOrder,valueType,valueRange,valueCandidates);
        experiments.push(newExperiment);
    }
    labData = {'oldLabId':oldLabId,'labName':labName, 'classId':classId, 'labDescription':labDescription, 'experiments':experiments};
    return labData;
}

// Check if the experiment names have repetition
function checkExperimentRepetition(experiments){
    // we use slice to clone the array so the original array won't be modified
    var sorted_experiments = experiments.slice().sort();
    var repetitions = '';
    for (var i = 0; i < experiments.length - 1; i++) {
        if (sorted_experiments[i + 1].name == sorted_experiments[i].name) {
            repetitions += ((i+1).toString()+'. '+sorted_experiments[i].name+'\n');
        }
    }
    return repetitions;
}

// --- Functions in student_select_lab.js ---
// Find the lab selected
function findLabSelected(radios){
    for (var i = 0; i < radios.length; i++) {
        if (radios[i].type == 'radio' && radios[i].checked) {
            labName = $(radios[i]).data('labname');   
            classId = $(radios[i]).data('classid');  
            className = decomposeClassId(classId)[0];
            professorName = $(radios[i]).data('profname');
            return generateLabId(labName,classId);
            break;
        }
    }
    return '';
}

// --- Functions in admin_select_lab_for_data.js ---
// Find all the labs selected
function findLabsSelected(labIds, checkBoxes){
    for (var i = 0; i < checkBoxes.length; i++) {
        if (checkBoxes[i].type == 'checkbox' && checkBoxes[i].checked) {
            labIds.push($(checkBoxes[i]).data('labid'));   
        }
    }
}

// --- Functions in admin_create_and_manage.js ---
function translateOperationToStatus(statusClassName){
    if (statusClassName == 'makeDownloadOnly'){
        return 'Downloadable';
    }
    else if (statusClassName == 'activateLab'){
        return 'Activated';
    }
    else if (statusClassName == 'deactivateLab'){
        return 'Unactivated';
    }
}

// --- Functions in admin_edit_data ---
// Extract observation data from all the input from user
function extractObservationData(allInput){
    oldObservationIdsList = []
    newObservationList = []
    for (var i=0;i<allInput.length;i++){
        if ($(allInput[i]).attr('class')!='studentName'){
            oldObservationIdsList.push($(allInput[i]).data('observationid'));
            var experimentId = $(allInput[i]).data('rowid');
            var studentName = $(allInput[i]).closest('tr').find(".studentName").val();
            var observationId = generateObservationId(experimentId,studentName);
            newObservationList.push({'experimentId':experimentId,'observationId':observationId,'studentName':studentName,'observationData':$(allInput[i]).val()})

        }
    }    
    return {'oldObservationIdsList': oldObservationIdsList,'newObservationList': newObservationList};  
}

function getObservationIdsToBeRemoved(ObservationsToBeRemoved){
        var observationIdsToBeRemoved = [];
        // Skip the first one(which is studentName)
        for (var i=1;i<ObservationsToBeRemoved.length;i++){
            observationIdsToBeRemoved.push($(ObservationsToBeRemoved[i]).data('observationid'));
        }
}

// --- Functions in general ---
// Check whether a string is in JSON format
function IsJsonString(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}
// The function will be invoked when an ajax request fails.
// It reports error by popping up a window and shows the error message returned from server
function errorReport(operation, result){
    console.log(result);
    errorMsg = '';
    result.responseText
    if (IsJsonString(result.responseText)){
        errorMsg = JSON.parse(result.responseText)['data'];
    }
    else{
        errorMsg = result.statusText;
    }
    $('#errorMsgsPopUp').html('Fail to '+operation+'<br>errorMsg: '+errorMsg+'<br>result: '+result);
    $('#errorPopup').modal("show");
}

// The function will be invoked when an ajax request succeeds but a warning message is returned.
// It reports error by popping up a window and shows the warning message returned from server
function warningReport(operation, result){
    console.log(result);
    warningMsg = '';
    if (IsJsonString(result.responseText)){
        warningMsg = JSON.parse(result.responseText)['data'];
    }
    else{
        warningMsg = result.statusText;
    }
    if (warningMsg != ''){
        $('#errorMsgs').html('Warning Message:<br>'+warningMsg);
        $('#errorPopup').modal('show');
    }
}
