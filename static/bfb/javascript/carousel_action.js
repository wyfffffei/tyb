$(function () {
    $($(".carousel-item")[0]).addClass("active");
    var pic = $(".contest_picture");
    var w = pic.width();
    var h = pic.height();
    var aw = w + 20;
    var ah = h + 20;
    $(pic).hover(function () {
        $(this).stop(true).animate({height: ah, width: aw, left: "-10px", top: "-10px"}, "fast");
    },function () {
        $(this).stop(true).animate({heigth: h, width: w, left: "0px", top: "0px"}, "fast");
    });

    var pic_wall = $("#demo");
    var main = $(".contest_detail");

    var hov_ele1 = main.find("a")[0];
    $(hov_ele1).hover(function () {
        $(this).parent().stop(true).animate({left: "10px"});
        $(this).prev().css("visibility", "visible");
        pic_wall.carousel(0);
    },function () {
        $(this).parent().stop(true).animate({left: "0px"});
        $(this).prev().css({visibility: "hidden"});
    });

    var hov_ele2 = main.find("a")[1];
    $(hov_ele2).hover(function () {
        $(this).parent().stop(true).animate({left: "10px"});
        $(this).prev().css({visibility: "visible"});
        pic_wall.carousel(1);
    },function () {
        $(this).parent().stop(true).animate({left: "0px"});
        $(this).prev().css({visibility: "hidden"});
    });

    var hov_ele3 = main.find("a")[2];
    $(hov_ele3).hover(function () {
        $(this).parent().stop(true).animate({left: "10px"});
        $(this).prev().css({visibility: "visible"});
        pic_wall.carousel(2);
    },function () {
        $(this).parent().stop(true).animate({left: "0px"});
        $(this).prev().css({visibility: "hidden"});
    });

    var hov_ele4 = main.find("a")[3];
    $(hov_ele4).hover(function () {
        $(this).parent().stop(true).animate({left: "10px"});
        $(this).prev().css({visibility: "visible"});
        pic_wall.carousel(3);
    },function () {
        $(this).parent().stop(true).animate({left: "0px"});
        $(this).prev().css({visibility: "hidden"});
    });
});