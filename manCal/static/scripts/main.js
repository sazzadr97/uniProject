
$("#favCategoriesSubmit").click(function(){
    $.ajax({
        type: 'DELETE',
        url: '/deleteFavCategories/',
        success: function (response) {
            $('#favCategoriesSelection > option:selected').each(function() {
                idCategory = $(this).val()
                $.ajax({
                    type: 'POST',
                    url: '/addFavCategory/',
                    data: {
                        'idCategory': idCategory
                    },
                    success: function (response) {
                    },
                    error: function (response) {
                        alert("Errorr");
                    }
                })
            });
            alert("Favourite categories saved.")
        },
        error: function (response) {
            alert("Errorr");
        }
    })
    preventDefault();
})

$('#img_file').change(function(){
    if ($('#img_file').get(0).files.length === 0) {
        $("#editPicBtn").hide();
    }
    else{
        $("#editPicBtn").show();
    }
})



$(function () {
    $("#editPicBtn").click(function uploadFile() {
       var formdata = new FormData();
       var file = document.getElementById('img_file').files[0];
       formdata.append('img_file', file);
       if(file){
            $.ajax({
                type : 'POST',
                url  : '/uploadimage/',
                data : formdata,
                success: function(data) {
                    location.reload(true);
                    $('#profile-img').attr("src",data);
                },
                processData : false,
            contentType : false,
            });
        }
        else{
            alert("Choose a picture");
            event.preventDefault();
        }
       
    });
});

if($('#deletePicBtn').is(":visible")){
    $("#editPicBtn").show();
}

$(function () {
    $("#deletePicBtn").click(function deleteFile() {
       $.ajax({
          type : 'DELETE',
          url  : '/deleteImage/',
          success: function(data) {
            location.reload(true);
          },
          processData : false,
          contentType : false,
       });
       event.preventDefault();
    });
});
