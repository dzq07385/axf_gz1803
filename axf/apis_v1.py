from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, QueryDict
from django.urls import reverse

from .models import *
from django.views.generic import View
from django.core.cache import cache
from .my_util import send_verify_mail, get_cart_sum_money
import logging

logger = logging.getLogger('django')

SUCCESS = 1
FAIL = 2
NOT_LOGIN = 3
GOODS_LACK = 4
GOODS_NOT_EXISTS = 5

DATA = {
    'code': SUCCESS,
    'msg': 'ok',
    'data': ''
}

class RegisterAPI(View):

    def post(self, req):
        # 解析参数
        param = req.POST
        u_name = param.get("u_name")
        pwd = param.get("pwd")
        confirm_pwd = param.get("confirm_pwd")
        email = param.get("email")
        icon = req.FILES['icon']

        # 对数据做校验
        if len(u_name) <= 4:
            return HttpResponse("账号名过短")
        if pwd and len(pwd) > 0 and pwd == confirm_pwd:
            if MyUser.objects.filter(username=u_name).exists():
                return HttpResponse("用户已存在")
            else:
                # 创建用户
                user = MyUser.objects.create_user(
                    username=u_name,
                    password=pwd,
                    email=email,
                    is_active=False,
                    icon=icon
                )
                #生成验证连接 发送邮件
                token = send_verify_mail(email, req.get_host())
                # 记录邮件和随机字符的验证邮箱
                cache.set(token, user.id, settings.EMAIL_TOKEN_MAX_AGE)
                return redirect(reverse("axf:login_view"))


#登录API
class LoginAPI(View):
    def post(self, req):
        params = req.POST
        # 'user_name': u_name,
        # 'pwd': enc_data
        # 解析参数
        u_name = params.get("user_name")
        pwd = params.get("pwd")
#         校验数据
        if pwd and u_name and len(u_name) >= 4:
            # 校验用户
            user = authenticate(username=u_name, password=pwd)
            print(user)
            if user:
                # 校验通过 就让用户登录
                login(req, user)
                # 返回跳转的连接
                DATA['data'] = "/axf/mine"
                DATA['code'] = SUCCESS
                return JsonResponse(DATA)
            else:
                # 如果校验失败 给出提示信息
                DATA['code'] = FAIL
                DATA['msg'] = '账号或密码错误'
                return JsonResponse(DATA)
        else:
            DATA['code'] = FAIL
            DATA['msg'] = "账号或密码不能为空"
            return JsonResponse(DATA)


def active(req, token):
    # 在缓存尝试拿数据
    user_id = cache.get(token)
    if user_id:
        # 如果拿到用户 那就修改用户的激活状态
        MyUser.objects.filter(pk=int(user_id)).update(is_active=True)
        return redirect(reverse("axf:login_view"))
    else:
        return HttpResponse("链接不正确或失效")

class LogoutAPI(View):

    def get(self, req):
        # 退出
        logout(req)
        return redirect(reverse('axf:home'))


def cart_api(req):
    # 拿用户
    user = req.user
    if not isinstance(user, MyUser):
        DATA['code'] = NOT_LOGIN
        DATA['msg'] = "尚未登录"
        DATA['data'] = "/axf/login"
        return JsonResponse(DATA)
    params = req.POST
    goods_id = params.get("g_id")
    operate_type = params.get("operate_type")
    # 拿商品
    item = Goods.objects.get(pk=int(goods_id))
    # 先去查查购物车
    cart_goods = Cart.objects.filter(
        user=user,
        goods_id=item.id
    )

    if operate_type == "add":
        # 检查库存
        if item.storenums <= 0:
            DATA['code'] = GOODS_LACK
            DATA['msg'] = "库存不足"
            return JsonResponse(DATA)

        if cart_goods.exists():
            # 不是第一次加购物车的情况
            # 拿到原来商品商品的数量
            tmp = cart_goods.first().num
            cart_goods.update(
                num=tmp+1
            )
            DATA['data'] = tmp + 1
        else:
            Cart.objects.create(
                user=user,
                goods_id=item.id,
                num=1
            )
            DATA["data"] = 1
            DATA['code'] = SUCCESS
            DATA['msg'] = 'ok'

        return JsonResponse(DATA)
    else:
        if cart_goods.exists():
            # 获取购物车的那个商品数据
            cart_item = cart_goods.first()
            # 将商品对应的数量减1
            cart_item.num = cart_item.num - 1
            if cart_item.num <= 0:
                cart_item.delete()
                # 在log里记录一下谁 把什么在购物车去掉了
                log_str = "{u_name}把{item_name}在购物车删掉了".format(
                    u_name=user.username,
                    item_name=item.productname
                )
                logger.info(log_str)
                DATA['data'] = 0
                return JsonResponse(DATA)
            else:
                # 如果数量没到0 那要保存数据
                cart_item.save()
                # 告诉前端当前数量
                DATA['data'] = cart_item.num
                return JsonResponse(DATA)
        else:
            DATA['msg'] = "都到0了 你点毛线啊"
            DATA['code'] = GOODS_NOT_EXISTS
            return JsonResponse(DATA)


def cart_item_api(req):
    user = req.user
    if not isinstance(user, MyUser):
        DATA['code'] = NOT_LOGIN
        DATA['msg'] = "未登录"
        DATA['data'] = "/axf/login"
        return JsonResponse(DATA)

    param = req.POST
    c_id = int(param.get("c_id"))
    operate_type = param.get("operate_type")

    # 获取购物车数据
    cart_item = Cart.objects.get(pk=c_id)
    if operate_type == 'add':
#         还要去判断库存
        if cart_item.goods.storenums <= 0:
            DATA['code'] = GOODS_LACK
            DATA["msg"] = "库存不足"
            DATA["data"] = ""
            return JsonResponse(DATA)
        # 商品数量加一
        cart_item.num += 1
        cart_item.save()

        # 拿到这个人购物车内全部选中商品
        money_sum = get_cart_sum_money(user)
        # 判断全选按钮的状态
        is_unselect = Cart.objects.filter(
            user=user,
            is_select=False
        ).exists()

        DATA['code'] = SUCCESS
        DATA['msg'] = "ok"
        DATA['data'] = {'current_num': cart_item.num,
                        'money': money_sum,
                        'is_un_all_select': is_unselect}
        return JsonResponse(DATA)
    else:
        # 将商品数量减一
        cart_item.num -= 1
        # 提前保存商品的数量
        cart_item_num = cart_item.num

        # 如果你商品数量到0 那就删除数据
        if cart_item.num <= 0:
            cart_item.delete()
        else:
            cart_item.save()
        # 算钱
        money_sum = get_cart_sum_money(user)
        # 判断全选按钮的状态
        is_unselect = Cart.objects.filter(
            user=user,
            is_select=False
        ).exists()
        DATA['code'] = SUCCESS
        DATA['msg'] = "ok"
        DATA['data'] = {'current_num': cart_item_num,
                        'money': money_sum,
                        'is_un_all_select': is_unselect}
        return JsonResponse(DATA)


class CartItemStatusAPI(View):

    def put(self, req):
        # 拿put请求参数
        param = QueryDict(req.body)
        c_id = int(param.get("c_id"))

        # 拿用户
        user = req.user
        if not isinstance(user, MyUser):
            DATA['code'] = NOT_LOGIN
            DATA['msg'] = "未登录"
            DATA['data'] = '/axf/login'
            return JsonResponse(DATA)
        # 找购车数据
        cart_data = Cart.objects.get(pk=c_id)
        # 将状态取反
        cart_data.is_select = not cart_data.is_select
        # 修改完数据状态 需要保存
        cart_data.save()
        # 算钱
        sum_money = get_cart_sum_money(user)

        # 判断是否全选  他未选中的数据是否存在
        is_all_select = not Cart.objects.filter(
            user=user,
            is_select=False
        ).exists()
        # 返回数据跟前端
        DATA['code'] = SUCCESS
        DATA['msg'] = 'ok'
        DATA['data'] = {
            'is_all_select': is_all_select,
            'sum_money': sum_money,
            'current_item_status': cart_data.is_select
        }
        return JsonResponse(DATA)


class CartAllItemStatusAPI(View):

    def put(self, req):
        param = QueryDict(req.body)
        user = req.user
        if not isinstance(user, MyUser):
            DATA['code'] = NOT_LOGIN
            DATA['data'] = '/axf/login'
            DATA['msg'] = '未登录'
            return JsonResponse(DATA)
        operate_type = param.get("o_type")
        sum_money = 0
        if operate_type == "select":
            # 将未选中的数据查询出来 通过update方法 更新状态
            Cart.objects.filter(
                user=user,
                is_select=False
            ).update(is_select=True)
            # 算钱
            sum_money = get_cart_sum_money(user)
        else:
            # 将已选中的数据查询出来 通过update方法 更新状态
            Cart.objects.filter(
                user=user,
                is_select=True
            ).update(is_select=False)
            # 算钱 默认就是0元

        #    返回结果
        DATA['code'] = SUCCESS
        DATA['msg'] = "ok"
        DATA['data'] = {
            'sum_money': sum_money,
            'is_all_select': operate_type
        }
        return JsonResponse(DATA)

