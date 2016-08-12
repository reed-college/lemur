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