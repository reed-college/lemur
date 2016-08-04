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
                  err_msg = JSON.parse(result.responseText)['data'];
                  $('#errorMsgs').html('Fail to delete<br>'+err_msg);
                  $('#errorPopup').modal("show");
                  console.log('Fail to delete');
                  console.log(result);
                }
        });
        $(this).closest('tr').remove();
        location.reload();
    }); 

    $('button[name=save]').click(function(){
          var classId = $(this).closest('tr').attr('id');
          var professorUserNames = $(this).closest('tr').find('select[name=professors]').val();
          var studentUserNames = $(this).closest('tr').find('select[name=students]').val();
          $.ajax({
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            url: 'http://127.0.0.1:5000/_superadmin_modify_class',
            data: JSON.stringify({'classId':classId,'studentUserNames':studentUserNames,'professorUserNames':professorUserNames}),
            success: function(result){
                    console.log('Save successfully');
                  },
            error : function(result){
                    err_msg = JSON.parse(result.responseText)['data'];
                    $('#errorMsgs').html('Fail to save<br>'+err_msg);
                    $('#errorPopup').modal("show");
                    console.log('Fail to save');
                    console.log(result);
                  }
          });
    });     
});
