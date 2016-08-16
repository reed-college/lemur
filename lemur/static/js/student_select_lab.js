$(document).ready(function(){
    $('button[name=goToLab]').click(function(){
        var radios = document.getElementsByTagName('input');
        // Find the lab selected by the user
        labId = findLabSelected(radios);
        if (labId==''){
            $('#errMsgNoLabChoosed').show().delay(1000).fadeOut();
        }
        else{
            window.location.replace('/student_data_entry/'+labId);
        }
    });
});
