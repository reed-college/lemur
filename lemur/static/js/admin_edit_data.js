$(document).ready(function(){
    $('button[name=saveAll]').click(function(){
        //Collect all the data in the table
        var allInput = document.getElementsByTagName('input');
        var observationData = extractObservationData(allInput);
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: '/_admin_change_data',
          data: JSON.stringify(observationData),
          success: function(result){
                    console.log('Change data successfully');
                    setTimeout(location.reload.bind(location), 100);
                },
          error : function(result){
                    errorReport('save data', result);
                }
        });
    });
    // The reason that we use javascript to show the modal rather than html is that this enables us
    // to show the modal that is closest to the delete button such that the modal is within the tr
    // that we want to delete
    $('.deleteData').click(function(){
        $(this).closest('tr').find('#deleteConfirm').modal("show");
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
                    $(this).closest('tr').remove();
                    setTimeout(location.reload.bind(location), 100);
                },
          error : function(result){
                    errorReport('delete data', result);
                }
        });
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
