$(function () {
    $(".add").click(function () {
        var $current_btn = $(this);
        var c_id = $(this).parents("li").attr("c_id");
        $.ajax({
            url:"/axf/api/v1/cart_item",
            data:{
                'c_id': c_id,
                'operate_type': 'add'
            },
            method:"post",
            success:function (res) {
                console.log(res);
                if (res.code == 1) {
                    var current_num = res.data.current_num;
                    var money = res.data.money;
                    //修改显示的数量
                    $current_btn.prev().html(current_num);
                    // 修改 总价
                    $("#money_id").html(money);
                     //修改全选按钮的状态
                    if (res.data.is_un_all_select) {
                        $(".all_select>span>span").html("");
                    } else {
                        $(".all_select>span>span").html("√");
                    }
                } else if (res.code == 3){
                    window.open(url=res.data, target="_self")
                } else {
                    alert(res.msg);
                }


            }
        });
    });
    $(".sub").click(function () {
        var $current_btn = $(this);
        var c_id = $(this).parents("li").attr("c_id");
        $.ajax({
            url:"/axf/api/v1/cart_item",
            data:{
                'c_id': c_id,
                'operate_type': 'sub'
            },
            method:"post",
            success:function (res) {
                console.log(res);
                if (res.code == 1) {
                    var current_num = res.data.current_num;
                    var money = res.data.money;
                    if (current_num <= 0 ){
                        //如果减到0了 删除对应li
                        $current_btn.parents("li").remove();
                    } else {
                        //修改显示的数量
                        $current_btn.next().html(current_num);
                    }
                    //修改全选按钮的状态
                    if (res.data.is_un_all_select) {
                        $(".all_select>span>span").html("");
                    } else {
                        $(".all_select>span>span").html("√");
                    }

                    // 修改 总价
                    $("#money_id").html(money);
                } else if (res.code == 3){
                    window.open(url=res.data, target="_self")
                } else {
                    alert(res.msg);
                }


            }
        });
    });
    
//    给选中按钮添加点击事件
    $(".confirm").click(function () {
        var c_id = $(this).parents("li").attr("c_id");
        //记录当前点击的那个按钮
        var $current_btn = $(this);
        $.ajax({
            url: "/axf/api/v1/cart_item_status",
            data:{
                'c_id': c_id
            },
            method: 'put',
            success:function (res) {
                // 'is_all_select': is_all_select,
            // 'sum_money': sum_money,
            // 'current_item_status'
                if (res.code == 1){
                    var sum_money = res.data.sum_money;
                    var is_all_select = res.data.is_all_select;
                    var current_item_status = res.data.current_item_status;

                //    更新总价
                    $("#money_id").html(sum_money);
                //    更新全选按钮
                    if (is_all_select){
                        $(".all_select > span > span").html("√");
                    } else {
                        $(".all_select > span > span").html("");
                    }
                //更新当前商品选中状态
                    if (current_item_status){
                        $current_btn.find("span").find("span").html("√");
                    } else {
                        $current_btn.find("span").find("span").html("");
                    }
                }
                else if (res.code == 3) {
                    //如果没登陆 就跳转到登录页面
                    window.open(url=res.data, target="_self");
                } else {
                    //其他情况提示错误信息
                    alert(res.msg);
                }
            }
        });
    });
//    给全选按钮加点击事件
    $(".all_select").click(function () {
    //    先去判断 当前的选中状态
        var select_str = $(".all_select>span>span").html();
        var all_select = "unselect";
        //如果全选标签里面的span 是空 那说明是未全选状态
        if (select_str.length == 0){
            all_select = "select";
        }
        //发送请求
        $.ajax({
            url: "/axf/api/v1/cart_all_select",
            data:{
                o_type: all_select
            },
            method:"put",
            success:function (res) {
                console.log(res);
                if (res.code == 1){
                    //判断更新全选按钮的状态
                    if (res.data.is_all_select == 'select'){
                        $(".all_select>span>span").html("√");
                        //循环遍历 修改商品的选中状态
                        $(".confirm").each(function () {
                            $(this).find("span").find("span").html("√");
                        })
                    } else {
                        $(".all_select>span>span").html("");
                        $(".confirm").each(function () {
                            $(this).find("span").find("span").html("");
                        })
                    }
                //    修改总价
                    $("#money_id").html(res.data.sum_money);
                }
            }
        });
    })
})