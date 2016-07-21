
$(document).ready(function(){       
    $('button[name=delete]').click(function(){
        var adminIdToBeRemoved = $(this).closest('tr').attr('id');
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: 'http://127.0.0.1:5000/_superadmin_delete_admin',
          data: JSON.stringify({'adminIdToBeRemoved':adminIdToBeRemoved}),
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
});
