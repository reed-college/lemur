$(document).ready(function(){ 
    // Toggle the accordion
    $(function(){
        $( "#accordion" ).accordion({
            collapsible: true,
            heightStyle: "content"
        });
    });
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
          var message = $(this).attr('id'); 
          var classIds = $(this).closest('div').find('select[name=classIdsForUpdate]').val();
          $.ajax({
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            url: '/_superadmin_update_info_from_iris',
            data: JSON.stringify({'message': message, 'classIds': classIds}),
            success: function(result){
                      console.log('Send data to server successfully:' + message + ', ' + classIds);
                      warningReport(message, result);
                  },
            error : function(result){
                      errorReport('send data to server', result);
                  }
          });
    });
});
