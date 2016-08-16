$(document).ready(function(){       
    $('button[name=delete]').click(function(){
        var classIdToBeRemoved = $(this).closest('tr').attr('id');
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: '/_superadmin_delete_class',
          data: JSON.stringify({'classIdToBeRemoved':classIdToBeRemoved}),
          success: function(result){
                    console.log('Delete successfully');
                },
          error : function(result){
                    errorReport('delete class', result);
                }
        });
        $(this).closest('tr').remove();
        location.reload();
    }); 

    $('button[name=save]').click(function(){
          var classId = $(this).closest('tr').attr('id');
          var professorUserNames = $(this).closest('tr').find('select[name=professors]').val();
          var studentUserNames = $(this).closest('tr').find('select[name=students]').val();
          var classInfo = {'classId':classId,'studentUserNames':studentUserNames,'professorUserNames':professorUserNames};
          $.ajax({
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            url: '/_superadmin_modify_class',
            data: JSON.stringify(classInfo),
            success: function(result){
                      console.log('Save successfully');
                  },
            error : function(result){
                      errorReport('save class', result);
                  }
          });
    });     
});
