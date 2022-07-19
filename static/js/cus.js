$(document).ready(function () {
  $('.enroll-btn').click(function (e) {
    // e.preventDefault();

    var course_id = $('input[name=course_id]').val();
    // var token = $('input[name=csrfmiddlewaretoken]').val();
    console.log(course_id)

    $.ajax({
      method: "GET",
      url: "/enroll",
      data: {
        'course_id': course_id,
      },
      // datatype: "dataType",
      success: function (response) {
        console.log(response.status);
      },
      error: (e)=>{
        console.log(e)
      }
    })
   
  })
})