
$(document).ready(function(){
    $('button[name=goToLab]').click(function(){
        var labIds = [];
        var checkBoxes = document.getElementsByTagName('input')
        for (var i = 0; i < checkBoxes.length; i++) {
            if (checkBoxes[i].type == 'checkbox' && checkBoxes[i].checked) {
                labIds.push($(checkBoxes[i]).data('labid'));   
            }
        }
        if (labIds.length==0){
            $('#errMsgNoLabchoosed').show().delay(1000).fadeOut();
        }
        else{
            //Redirect to the page that shows the data of the selected labs
            window.location.replace('/admin_edit_data/'+JSON.stringify(labIds));
        }

    });
});
