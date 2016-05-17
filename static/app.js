$(function () {
    $("#xkcd-form").submit(function (event) {
        event.preventDefault();
        $("#content").html("<div class='loader'>Loading...</div>");
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
