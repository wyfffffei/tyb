$(function () {
    <!-- 生成随机ID -->
    function S4() {
        return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    }
    function guid() {
        return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
    }
    let option = Array();
    $(".del_team").each(function () {
        $(this).attr("id", guid());
        option.push($(this).attr("id"));
    });
    for (let i=0;i<option.length;i++){
        $("#"+option[i]).confirm({
            title: '<p style="color: red">提示</p>',
            content: '<p style="color: gray">确定删除该球队吗？该操作可能无法恢复！</p>',
            buttons: {
                "确认": function () {
                    $("#"+option[i]).parent().submit();
                },
                "再看看": function () {},
            }
        });
    }
})