$(document).ready(function(){    
    $('button[name=saveAll]').click(function(){
        //Collect all the data in the table
        oldObservationIdsList = []
        newObservationList = []
        var allInput = document.getElementsByTagName('input');
        for (var i=0;i<allInput.length;i++){
            if ($(allInput[i]).attr('class')!='studentName'){
                oldObservationIdsList.push($(allInput[i]).data('observationid'));
                var experimentId = $(allInput[i]).data('rowid');
                var studentName = $(allInput[i]).closest('tr').find(".studentName").val();
                var observationId = generateObservationId(experimentId,studentName);
                newObservationList.push({'experimentId':experimentId,'observationId':observationId,'studentName':studentName,'observationData':$(allInput[i]).val()})

            }
        }       
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: 'http://127.0.0.1:5000/_admin_change_data',
          data: JSON.stringify({'oldObservationIdsList':oldObservationIdsList,'newObservationList':newObservationList}),
          success: function(result){
                    console.log('Change successfully');
                },
          error : function(result){
                    err_msg = JSON.parse(result.responseText)['data'];
                    $('#errorMsgs').html('Fail to save change<br>'+err_msg);
                    $('#errorPopup').modal("show");
                    console.log('Fail to change');
                    console.log(result);
                }
        });
        location.reload();

    });

    $('button[name=confirm]').click(function(){
        var observationIdsToBeRemoved = [];
        var trId = $(this).closest('tr').attr('id');
        console.log(trId);
        var ObservationsToBeRemoved = document.getElementById(trId).getElementsByTagName('input');
        // Skip the first one(which is studentName)
        for (var i=1;i<ObservationsToBeRemoved.length;i++){
            console.log($(ObservationsToBeRemoved[i]).data('observationid'));
            observationIdsToBeRemoved.push($(ObservationsToBeRemoved[i]).data('observationid'));
        }
        $.ajax({
          type: 'POST',
          contentType: 'application/json',
          dataType: 'json',
          url: 'http://127.0.0.1:5000/_admin_delete_data',
          data: JSON.stringify({'observationIdsToBeRemoved':observationIdsToBeRemoved}),
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
    
    $('button[name=download]').click(function(){
        var undownloadableLabs = $('table').data('undownloadable').split(',').join('<br>');
        if (undownloadableLabs==''){
            lab_ids = $('table').attr('id').split(',');
            console.log(lab_ids);
            window.location.replace('/_admin_download_data/'+JSON.stringify(lab_ids));
        }
        else{
            $('#errorMsgsDownload').html('The following lab(s):<br>'+undownloadableLabs+
              ' are not downloadable.<br>Please change its status to downloadable on'+
              ' <b>Add a New Lab page<b>');
            $("#errorPage").modal("show");
        } 
    });
});