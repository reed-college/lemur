
$(document).ready(function(){
    // Toggle the accordion
    $(function(){
        $( "#accordion" ).accordion({
            collapsible: true,
            heightStyle: "content"
        });
    });

    // Modify an existing lab
    $('.modifyLab').click(function(){
        var labId = $(this).closest('tr').data('labid');
        window.location.replace('/admin_modify_lab/'+labId);        
    });
    
    // The reason that we use javascript to show the modal rather than html is that this enables us
    // to show the modal that is closest to the delete button such that the modal is within the tr
    // that we want to delete
    $('.deleteLab').click(function(){
        $(this).closest('tr').find('#deleteConfirm').modal("show");
    });

    // Duplicate/Delete a lab
    $('.duplicateLab').add($('button[name=confirm]')).click(function(){
        var operation = $(this).data('operation');
        var labId = $(this).closest('tr').data('labid');
        // Communicate the name of the lab to be duplicated with python via Ajax 
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: '/_admin_'+operation,
          data: JSON.stringify({'labId':labId}),
          success: function(result){
                    console.log(operation+' successfully');
                    setTimeout(location.reload.bind(location), 100);
               
                },
          error : function(result){
                    errorReport(operation, result);
                }
        });
        setTimeout(location.reload.bind(location), 100);
        if (operation=='delete_lab'){
            $(this).closest('tr').remove();
        }
    });

    //Change a lab's status
    $('.makeDownloadOnly').add($('.activateLab')).add($('.deactivateLab')).click(function(){
        var labId = $(this).closest('tr').data('labid');
        var statusClassName = $(this).attr('class')
        var newStatus = translateOperationToStatus(statusClassName);
        
        //Communicate the name of the lab to be duplicated with python via Ajax 
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: '/_admin_change_lab_status/'+newStatus,
          data: JSON.stringify({'labId':labId}),
          success: function(result){
                    console.log('Change lab status successfully');
                    setTimeout(location.reload.bind(location), 100);
                },
          error : function(result){
                    errorReport('change lab status', result);
                }
        });
        setTimeout(location.reload.bind(location), 100);  
    });

});
