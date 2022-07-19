$(document).ready(function () {

  $('.bulk-btn').click(function (e) {
    // e.preventDefault();

    var course_id = $('input[name=course_id]').val();
    var token = $('input[name=csrfmiddlewaretoken]').val();

    $.ajax({
      method: "POST",
      url: "/bulk",
      data: {
        'course_id': course_id,
        csrfmiddlewaretoken: token,
      },
      // datatype: "dataType",
      success: function (response) {
        Swal.fire(
          response.heading,
          response.message,
          response.status
        )
      },
      error: function (e) {
        Swal.fire(
         'Error',
          e.statusText,
          'warning'
        )
      }
    })
   
  })
 
})