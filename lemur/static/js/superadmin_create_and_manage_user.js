$(document).ready(function(){ 
    $('button[name=delete]').click(function(){
        var userIdToBeRemoved = $(this).closest('tr').attr('id');
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: 'http://127.0.0.1:5000/_superadmin_delete_user',
          data: JSON.stringify({'userIdToBeRemoved':userIdToBeRemoved}),
          success: function(result){
                  console.log('Delete successfully');
                },
          error : function(result){
                    err_msg = JSON.parse(result.responseText)['data'];
                    $('#errorMsgs').html('Fail to delete<br>'+err_msg);
                    $('#errorPopup').modal("show");
                    console.log('Fail to delete');
                    console.log(result)
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
            url: 'http://127.0.0.1:5000/_superadmin_change_user_info',
            data: JSON.stringify({'username':username,'role':role,'classIds':classIds}),
            success: function(result){
                    console.log('Save successfully');
                  },
            error : function(result){
                      err_msg = JSON.parse(result.responseText)['data'];
                      $('#errorMsgs').html('Fail to save<br>'+err_msg);
                      $('#errorPopup').modal('show');
                      console.log('Fail to save');
                      console.log(result);
                  }
          });   
          location.reload();      
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
                      warning_msg = JSON.parse(result.responseText)['data'];
                      console.log('Send data to server successfully:' + message);
                      if (warning_msg != ''){
                          $('#errorMsgs').html('Warning Message:<br>'+warning_msg);
                          $('#errorPopup').modal('show');
                      }
                  },
            error : function(result){
                      err_msg = JSON.parse(result.responseText)['data'];
                      $('#errorMsgs').html('Fail to send data to server<br>'+err_msg);
                      $('#errorPopup').modal('show');
                      console.log('Fail to send data to server:' + message);
                      console.log(result);
                  }
          });
    });

});
