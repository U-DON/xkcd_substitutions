$(function () {
    $("#xkcd-form").submit(function (event) {
        event.preventDefault();
        $("#content").html("<div class='loader'>Loading...</div>");
        $.get({
            url: "/xkcdify",
            data: {
                url: $("#url").val()
            },
            dataType: "html",
            success: function (data) {
                $("#content").html(data);
            },
            error: function (xhr, status, error) {
                $("#content").html("<h1>Whoops! Something went wrong...</h1>"
                                   + "<p>Unable to complete your request.</p>");
            },
            timeout: 5000
        });
    });
});
