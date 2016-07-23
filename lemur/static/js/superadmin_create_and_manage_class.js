
$(document).ready(function(){       
    $('button[name=delete]').click(function(){
        var classIdToBeRemoved = $(this).closest('tr').attr('id');
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: 'http://127.0.0.1:5000/_superadmin_delete_class',
          data: JSON.stringify({'classIdToBeRemoved':classIdToBeRemoved}),
          success: function(result){
                  console.log('Delete successfully');
                },
          error : function(result){
                  console.log('Fail to delete');
                  console.log(result);
                }
        });
        $(this).closest('tr').remove();
        location.reload();
    }); 
    $('button[name=saveAll]').click(function(){
        // Flag used to check the correctness of the input
        var wrongInput = false;
        // Submit form to report error if the input is illegal
        if (!$('#existingClasses')[0].checkValidity()){
            wrongInput=true;
            $('<input type="submit">').hide().appendTo($('#existingClasses')).click().remove();
        }

        if (!wrongInput){
            var classId = $(this).closest('tr').attr('id');
            var professorUserName = $(this).closest('tr').find('select').val();
            var studentUserNames = $(this).closest('tr').find('textarea').val();
            $.ajax({
              type: 'POST',
              contentType: 'application/json',
              dataType: 'json',
              url: 'http://127.0.0.1:5000/_superadmin_modify_class',
              data: JSON.stringify({'classId':classId,'studentUserNames':studentUserNames,'professorUserName':professorUserName}),
              success: function(result){
                      console.log('Save successfully');
                    },
              error : function(result){
                      console.log('Fail to save');
                      console.log(result);
                    }
            });
        }           
    });     
});
