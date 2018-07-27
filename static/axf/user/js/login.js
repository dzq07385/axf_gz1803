$(function () {
    $("#submit").click(function () {
        //拿用户输入的数据
        var u_name = $("#u_name").val();
        var $pwd = $("#u_pwd");
        //校验用户名长度
        if (u_name.length <= 4){
            alert("用户名过短");
            return;
        }
        //校验密码长度
        if ($pwd.val().length >= 4 ){
            //加密密码
            var enc_data = md5($pwd.val());
        //    发送Ajax请求
            $.ajax({
                url:"/axf/api/v1/login",
                data:{
                    'user_name': u_name,
                    'pwd': enc_data
                },
                method: 'post',
                success:function (res) {
                    console.log(res);
                    if (res.code == 1) {
                        //跳转
                        window.open(url=res.data, target="_self");
                    } else {
                        alert(res.msg);
                    }
                }
            })
        }

    });
})