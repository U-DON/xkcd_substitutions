$(function () {
    $("#xkcd-form").submit(function (event) {
        event.preventDefault();
        // Loading animation...
        $.get({
            url: "/generate",
            data: {
                url: $("#url").val()
            },
            dataType: "html",
            success: function (data) {
                $("#content").html(data);
            }
        });
    });
});
