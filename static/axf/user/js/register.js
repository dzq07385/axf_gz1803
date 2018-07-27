$(function () {
    $("#my_form").submit(function () {
        //拿用户名的数据
        var u_name = $("#u_name").val();
        var $pwd = $("#u_pwd");
        var $confirm  = $("#u_confirm_pwd");
        if (u_name.length <= 4){
            alert("用户名过短");
            return false;
        }
        if ($pwd.val() == $confirm.val() && $pwd.val().length>=4){
            //将密码做加密
            var enc_data = md5($pwd.val());
            $pwd.val(enc_data);
            $confirm.val(enc_data);
        } else {
            alert("密码不符合规范");
            return false;
        }
    });
})