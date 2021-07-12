$(function () {
    // 页面css
    $("#directory").css({"background": "rgba(127,62,252,0.62)"});
    $("#home .text-secondary").css({"font-size": "25px"});
    $("#score .text-secondary").css({"font-size": "16px"});
    // 留言板js
    $(".message").click(function () {
        let login_flag = "{{ is_login|safe }}";
        if (login_flag == "True"){
            $.confirm({
                title: '为球队加油！',
                content: '' + '<form id="note_form" method="post">{% csrf_token %}' + '<div class="form-group">' + '<label></label>' + '<input type="text" placeholder="湖人总冠军.." name="note" class="note form-control" maxlength="200" required/>' + '</div>' + '</form>',
                buttons: {
                    formSubmit: {
                        text: '提交',
                        btnClass: 'btn-blue',
                        action: function () {
                            let words = this.$content.find('.note').val();
                            if(!words){
                                $.alert({
                                    title: '提示',
                                    content: '请提交完整表单！',
                                    type: 'orange',
                                });
                                return false;
                            }
                            $("#note_form").submit();
                        }},
                    "取消": function () {
                        //close
                    },
                },
            });
        }
        else {
            $.alert({
                title: '提示',
                content: '请先登录！',
                type: 'orange',
            });
        }
    })
})