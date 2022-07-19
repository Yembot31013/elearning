

  $(document).ready(function () {
  $('.coupon-btn').click(function (e) {
    // e.preventDefault();

    var coupon = $('input[name=pay_id]').val();
    var codes = $('input[name=code]').val();
    var course = $('input[name=course]').val();
    var token = $('input[name=csrfmiddlewaretoken]').val();

    console.log("course", course);

    $.ajax({
      method: "POST",
      url: "coupon/",
      data: {
        "course": course,
        "coupon": coupon,
        "codes": codes,
        csrfmiddlewaretoken: token,
      },
      // datatype: "dataType",
      success: function (response) {
       location.reload()
      },
      error: function (e) {
        console.log(e)
      }
    })
  })
 
})