// Show Value Range/Value Type field according to user's choice of value Type field
function ShowFieldByChoice(){
    var selects = document.getElementsByClassName('valueType');
    for (var i = 0; i<selects.length; i++){
        var s = selects[i];
        var selectValue = s.getElementsByClassName('selectpicker')[0].value;
        var divText =  s.getElementsByClassName('valueCandidates')[0];
        var divValue =  s.getElementsByClassName('valueRange')[0];
        if (selectValue == 'Text') {
             divText.style.display = 'block';
             divValue.style.display = 'none';
        }
        else {
            divText.style.display = 'none';
            divValue.style.display = 'block';
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
var experiments = [];
$(document).ready(function(){
    // Show Value Range/Value Type field according to user's choice of value Type field
    // both when the doc is initialized and when user select another option
    ShowFieldByChoice();
    
    // Add a new experiment
    $('button[name=addExperiment]').click(function(){
        var existingExperiments = document.getElementsByClassName('experiment');
        var newIndexStr = (existingExperiments.length+1).toString();
        $('div[name=formBody]').append('<div class="col-lg-6 col-md-6 col-sm-6 mb experiment">'+
                                           '<h4>Question'+newIndexStr+':</h4>'+
                                           '<label> Name*: </label>'+
                                           '<input type="text" name="experimentName" pattern="'+PATTERN_FOR_NAME+'" title="'+PATTERN_FOR_NAME_HINT+'" required>'+
                                           '<br>'+
                                           '<label>Description:</label>'+
                                           '<br>'+
                                           '<textarea class="longInput" cols="30" rows="5" name="experimentDescription" pattern="'+PATTERN_FOR_EXPERIMENT_DESCRIPTION+'" title="'+PATTERN_FOR_EXPERIMENT_DESCRIPTION_HINT+'"></textarea>'+
                                           '<div class="valueType">'+
                                           '<label>Value Type*: </label>'+
                                           '<select class="selectpicker" name="valueType" required>'+
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
                                       '</div>');
    });
        
    //Delete an existing experiment by specifying the question number
    $('button[name=deleteExperiment]').click(function(){
        var experimentNameDeleted = $('input[name=questionDeleted]').val();
        $('.experiment[name='+experimentNameDeleted+']').remove();
    });
    //Submit labinfo
    $('button[name=saveChange]').click(function(){
        // Flag used to check the correctness of the input
        var wrongInput = false;
        // Validate all the input
        if (!($('#labForm')[0].checkValidity())){
          wrongInput=true;
          $('<input type="submit">').hide().appendTo($('#labForm')).click().remove();
        }
        
        if (wrongInput==false){
            // Collect all the input
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
            
            // Check if the experiment names have repetition
            // we use slice to clone the array so the original array won't be modified
            var sorted_experiments = experiments.slice().sort();
            var results = '';
            for (var i = 0; i < experiments.length - 1; i++) {
                if (sorted_experiments[i + 1].name == sorted_experiments[i].name) {
                    results += ((i+1).toString()+'. '+sorted_experiments[i].name+'\n');
                }
            }
            if (results){
                $('#errorMsgs').html('The following experiments have repetitions:<br>'+
                                     results+'<br>Please change them to make sure that they are unique.');
                $('#errorChecking').modal('show');
            }
            else{
                // Delete the old lab and save the new lab
                $.ajax({
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json',
                    url: 'http://127.0.0.1:5000/'+$('#labForm').data('postaddress'),
                    data: JSON.stringify({'oldLabId':oldLabId,'labName':labName, 'classId':classId, 'labDescription':labDescription, 'experiments':experiments}),
                    success: function(result){
                          console.log('Change successfully');
                    },
                    error : function(result){
                          console.log('Fail to change(lab id must be unique)');
                          console.log(result);
                    }
                  });
                // Redirect to the main page of setup lab and data access
                window.location.replace('/admin_setup_labs_and_data_access');

            }
            
            
        }
    });
});

// Make the change of Value Candidates/Value Range field dynamic
$(document).on('change', '.valueType', function(){
        ShowFieldByChoice();
});
   