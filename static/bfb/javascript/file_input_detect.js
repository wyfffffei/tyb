function test(pic_id, required_fileSize) {
    /* 后端图片上传 */
    var filePath = $("#"+pic_id).val();
    if (filePath) {
        var fileType = getFileType(filePath);
        // console.log(fileType);
        //判断上传的附件是否为图片
        if (fileType != "jpg" && fileType != "jpeg" && fileType != "png") {
            $("#"+pic_id).val("");
            alert("请上传JPG,JPEG或PNG格式的图片！");
            return false;
        } else {
            //获取附件大小（单位：KB）
            var fileSize = document.getElementById(pic_id).files[0].size / 1024;
            // console.log(fileSize);
            if (fileSize > required_fileSize) {
                alert("图片大小不能超过"+required_fileSize/1024+"MB!");
                return false;
            }
            else {
                return true;
            }
        }
    }
    else {
        return true;
    }
}
function getFileType(filePath) {
    var startIndex = filePath.lastIndexOf(".");
    if (startIndex)
        return filePath.substring(startIndex + 1, filePath.length).toLowerCase();
    else return "";
}
