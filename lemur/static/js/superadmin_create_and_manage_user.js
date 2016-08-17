$(document).ready(function(){ 
    $('button[name=delete]').click(function(){
        var userIdToBeRemoved = $(this).closest('tr').attr('id');
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: '/_superadmin_delete_user',
          data: JSON.stringify({'userIdToBeRemoved':userIdToBeRemoved}),
          success: function(result){
                    console.log('Delete successfully');
                },
          error : function(result){
                    errorReport('delete user', result);
                }
        });
        $(this).closest('tr').remove();
        location.reload();
    });  

    $('button[name=save]').click(function(){
          var username = $(this).closest('tr').attr('id');
          var role = $(this).closest('tr').find('select[name=role]').val();
          var classIds = $(this).closest('tr').find('select[name=classIds]').val();
          $.ajax({
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            url: '/_superadmin_change_user_info',
            data: JSON.stringify({'username':username,'role':role,'classIds':classIds}),
            success: function(result){
                      console.log('Save successfully');
                  },
            error : function(result){
                      errorReport('save user', result);
                  }
          });   
          //location.reload();      
    });  

    $('button[name=updateUserInfo]').add($('button[name=resetClass]')).click(function(){
          message = $(this).attr('id'); 
          $.ajax({
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            url: '/_superadmin_update_info_from_iris',
            data: JSON.stringify({'message': message}),
            success: function(result){
                      console.log('Send data to server successfully:' + message);
                      warningReport(message, result);
                  },
            error : function(result){
                      errorReport('send data to server', result);
                  }
          });
    });
});
