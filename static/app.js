$(function () {
    $(".preview").click(function () {
        var example = $(this).closest(".example");
        example.find("span.old-title").hide();
        example.find("span.new-title").show();
        this.disabled = true;
    });

    $(".convert").click(function () {
        var url = $(this).parent().siblings("a").attr("href");
        $("#url-input").val(url);
        $("#xkcd-form").submit();
    });

    $("#xkcd-form").submit(function (e) {
        e.preventDefault();
        var loader = $("<span>"
                       + "<i class='fa fa-refresh fa-spin'></i>"
                       + "<span class='sr-only'>Loading...</span>"
                       + "</span>");
        var button = $("#xkcd-form button");
        button.children().hide();
        button.append(loader);
        button.prop("disabled", true);
        $.get({
            url: "/xkcdify",
            data: {
                url: $("#url-input").val()
            },
            dataType: "html",
            success: function (data) {
                $("#content").html(data);
            },
            error: function (xhr, status, error) {
                var h1 = $("<h1>").text("Whoops! Something went wrong...");
                var p = $("<p>");
                if (status == "timeout") {
                    p.text("The request timed out.");
                }
                else {
                    p.text("Unable to complete your request");
                }
                $("#content").html("");
                $("#content").append(h1).append(p);
            },
            timeout: 5000
        }).complete(function () {
            loader.remove();
            button.children().show();
            button.prop("disabled", false);
        });
    });
});
