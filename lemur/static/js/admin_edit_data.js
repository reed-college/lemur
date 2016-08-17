$(document).ready(function(){    
    $('button[name=saveAll]').click(function(){
        //Collect all the data in the table
        var allInput = document.getElementsByTagName('input');
        var observationData = collectObservationData(allInput);
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: '/_admin_change_data',
          data: JSON.stringify(observationData),
          success: function(result){
                    console.log('Change data successfully');
                },
          error : function(result){
                    errorReport('save data', result);
                }
        });
        location.reload();
    });

    $('button[name=confirm]').click(function(){
        var trId = $(this).closest('tr').attr('id');
        var ObservationsToBeRemoved = document.getElementById(trId).getElementsByTagName('input');
        var observationIdsToBeRemoved = getObservationIdsToBeRemoved(ObservationsToBeRemoved);
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: '/_admin_delete_data',
          data: JSON.stringify({'observationIdsToBeRemoved':observationIdsToBeRemoved}),
          success: function(result){
                    console.log('Delete data successfully');
                },
          error : function(result){
                    errorReport('delete data', result);
                }
        });
        $(this).closest('tr').remove();
        location.reload();
    });     
    
    $('button[name=download]').click(function(){
        var undownloadableLabs = $('table').data('undownloadable').split(',').join('<br>');
        if (undownloadableLabs==''){
            lab_ids = $('table').attr('id').split(',');
            window.location.replace('/_admin_download_data/'+JSON.stringify(lab_ids));
        }
        else{
            $('#errorMsgsDownload').html('The following lab(s):<br>'+undownloadableLabs+
              ' are not downloadable.<br>Please change its status to downloadable on'+
              ' <b>Create/Manage Lab page<b>');
            $("#errorPage").modal("show");
        } 
    });
});