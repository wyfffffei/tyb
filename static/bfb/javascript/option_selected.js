function option_selected(jq_ele, data) {
    let ele = jq_ele;
    const da = data;

    let option_all = Array();
    $(ele.children()).each(function () {
        option_all.push($(this).val());
    });
    let flag = false;
    for (let i=0;i<option_all.length;i++){
        // console.log(option_all[i]);
        if (option_all[i] == da){
            // $(ele.children()).eq(i).val();
            $(ele.children()).eq(i).attr('selected',"selected");
            flag = true;
        }
    }
    if (flag){}
    else {$(ele.children()).last().attr('selected',"selected");}
}