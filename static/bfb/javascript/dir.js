function loadImg(url,callback){
    var img = new Image();
    img.onload = function(){
        img.onload = null;
        callback(img);
    }
    img.src=url;
}
function addImg(url){
    $("#bki").css('background-image', "url('"+url.src+"')");
}
$(function () {
    /* 顶部导航栏active样式 */
    $(".navbar-nav").find("li").each(function () {
        var a = $(this).find("a:first")[0];
        if ($(a).attr("href") === location.pathname) {
            $(this).addClass("active");
        } else {
            $(this).removeClass("active");
        }
    });
    /* products栏动画 */
    $("#pro_1").hover(function () {
        $(this).stop(true).animate({"backgroundColor":"#f15bb5"},"fast");});
    $("#pro_2").hover(function () {
        $(this).stop(true).animate({"backgroundColor":"#fee440",},"fast");});
    $("#pro_3").hover(function () {
        $(this).stop(true).animate({"backgroundColor":"#00bbf9",},"fast");});
    $("#pro_4").hover(function () {
        $(this).stop(true).animate({"backgroundColor":"#00f5d4",},"fast");});
    $(".product-head-content").hover(function () {
        $(this).children().not("span").stop(true).animate({
            opacity: "0"
        },"fast");
        $(this).find("span").stop(true).animate({
            top: "-125px",
            opacity: "1",
        },"fast");},function () {
        $(this).find("span").stop(true).animate({
            top: "0",
            opacity: "0"
        },"fast");
        $(this).children().not("span").stop(true).animate({
            opacity: "1"
        },"fast");
        $(this).stop(true).animate({"backgroundColor": "#f3f3f3",},"fast");
    });
});
