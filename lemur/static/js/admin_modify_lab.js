var experiments = [];

$(document).ready(function(){
    // Show Value Range/Value Type field according to user's choice of value Type field
    // both when the doc is initialized and when user select another option
    ShowFieldByChoice();
    
    // Reset Input field
    // The reason that we don't directly put the reset inside the form and use it directly
    // is for better formatting of the page
    $('button[name=resetLab]').click(function(){
        $('button[name=hiddenresetLab]').click();
    });

    // Add a new experiment
    $('button[name=addExperiment]').click(function(){
        var existingExperiments = document.getElementsByClassName('experiment');
        // newIndexStr represents the default number/order of the newly generated question
        var newIndexStr = (existingExperiments.length+1).toString();
        // Append new question to the form without refreshing the page/sending request to server
        $('div[name=formBody]').append(generateNewQuestion(newIndexStr));
        $('.selectpicker').selectpicker('render');
    });
        
    //Delete an existing experiment by specifying the question number
    $('button[name=deleteExperiment]').click(function(){
        var experimentNameDeleted = $('input[name=questionDeleted]').val();
        $('.experiment[name="'+experimentNameDeleted+'"]').remove();
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
            // Collect all the input for lab
            var labData = collectLabData();
            // Check if the experiment names have repetition and report error accordingly
            var repetitions = checkExperimentRepetition(labData['experiments']);
            if (repetitions){
                $('#errorMsgs').html('The following experiments have repetitions:<br>'+
                                     repetitions+'<br>Please change them to make sure that they are unique.');
                $('#errorChecking').modal('show');
            }
            else{
                // Delete the old lab and save the new lab
                $.ajax({
                    type: 'POST',
                    contentType: 'application/json',
                    dataType: 'json',
                    url: '/'+$('#labForm').data('postaddress'),
                    data: JSON.stringify(labData),
                    success: function(result){
                          console.log('Change lab successfully');
                          setTimeout(function() { 
                               redirectTo('/admin_create_and_manage_lab');
                          }, 50);
                    },
                    error : function(result){
                          errorReport('change lab', result);
                    }
                  });
            }
        }
    });
});

// Make the change of Value Candidates/Value Range field dynamic
$(document).on('change', '.valueType', function(){
        ShowFieldByChoice();
});
   
