
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
                    console.log('Fail to save');
                    console.log(result);
                  }
          });   
          location.reload();      
    });   
});



