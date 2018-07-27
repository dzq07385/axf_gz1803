$(function () {
    //二级分类按钮
    var type_icon_is_down = true;
    $("#all_type").click(function () {
        //
        type_icon_is_down = type_icon_toggle(type_icon_is_down);
        $("#type_containor").toggle();
    })
    $("#type_containor").click(function () {
        $(this).toggle();
        type_icon_is_down = type_icon_toggle(type_icon_is_down);
    })

//    排序按钮
    $("#all_sorted").click(function () {
        $("#sort_containor").toggle();
    })
    $("#sort_containor").click(function () {
        $(this).toggle();
    })

//    跟加号按钮添加点击事件
    $(".addShopping").click(function () {
        var g_id = $(this).attr("g_id");
        var $current_btn = $(this);
        $.ajax({
            url:"/axf/api/v1/cart",
            data:{
                g_id: g_id,
                operate_type: "add"
            },
            method:"post",
            success:function (res) {
                console.log(res);
                if (res.code == 1){
                //    我要更新span标签上边的数字
                    $current_btn.prev().html(res.data);

                } else if(res.code == 3){
                    //处理没登陆的情况
                    window.open(url=res.data, target="_self")
                } else {
                    alert(res.msg)
                }
            }
        });
    })

    //    跟减号按钮添加点击事件
    $(".subShopping").click(function () {
        var g_id = $(this).attr("g_id");
        var $current_btn = $(this);
        var span_str = $current_btn.next().text();
        if (parseInt(span_str) == 0){
            return ;
        }
        $.ajax({
            url:"/axf/api/v1/cart",
            data:{
                g_id: g_id,
                operate_type: "sub"
            },
            method:"post",
            success:function (res) {
                if (res.code == 1){
                //    我要更新span标签上边的数字
                    $current_btn.next().html(res.data);

                } else if(res.code == 3){
                    //处理没登陆的情况
                    window.open(url=res.data, target="_self")
                } else {
                    alert(res.msg)
                }
            }
        });
    })
})
function type_icon_toggle(type_icon_is_down) {
    if (type_icon_is_down){
            $("#type_icon").removeClass("glyphicon-chevron-down").addClass("glyphicon-chevron-up");
            type_icon_is_down = false;
        } else {
            $("#type_icon").removeClass("glyphicon-chevron-up").addClass("glyphicon-chevron-down");
            type_icon_is_down = true;
        }
        return type_icon_is_down;
}