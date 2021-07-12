function sign_error(error){
    if (error) {
        $.alert({
            title: '登录失败',
            content: error,
            type: 'red',
            typeAnimated: true,
            buttons: {'检查一下': function () {}}
        });
    }
}
function register_error(error){
    if (error) {
        $.alert({
            title: '注册失败',
            content: error,
            type: 'red',
            typeAnimated: true,
            buttons: {'检查一下': function () {}}
        });
    }
}
function publish_error(error) {
    if (error) {
        $.alert({
            title: '发布失败',
            content: error,
            type: 'red',
            typeAnimated: true,
            buttons: {'检查一下': function () {}}
        });
    }
}