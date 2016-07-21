// This file contains all the JS utility functions

function generateLabId(labName,className,professorName){
    return labName+'_'+className+'_'+professorName;
}
function generateObservationId(experimentId,studentName){
    return experimentId+':'+studentName;
}
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
    if (valueType=='Text' && valueCandidates.length>0){
        valueCandidates_arr = valueCandidates.split(',');
        if (!isInArray(observation,valueCandidates_arr)){
            wrongInput = true;
            if (observation == ''){ observation = NaN;}
            errMsg = observation+' is not in the value candidates: '+valueCandidates; 
        }        
    }
    else if (valueType=='Number' && valueRange.length>0){
        valueRangeArray = valueRange.split('-');
        var min = parseFloat(valueRangeArray[0]);
        var max = parseFloat(valueRangeArray[1]);
        var observation = parseFloat(observation);
        if (!isNumeric(observation)){
            wrongInput = true;
            errMsg = observation+' is not a number.';
        }
        else if (observation<min || observation>max){
            wrongInput = true;
            errMsg = observation+' is not in the value range: '+valueRange;
        }
    }
    return {'wrongInput':wrongInput,'errMsg':errMsg};
}
