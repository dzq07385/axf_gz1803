from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .models import *
from .my_util import get_cart_sum_money
import json

# Create your views here.
DEFAULT_SORT = 0
PRICE_SORT = 1
SALE_NUM_SORT = 2

def home(req):
    # 拿轮播数据
    swipers = MyWheel.objects.raw("SELECT * FROM axf_wheel")
    # 拿导航数据
    navs = MyNav.objects.all()
    # 拿必购的数据
    mustbys = MustBuy.objects.all()
    # 拿商店数据
    shops = MyShop.objects.all()
    shop_img = shops[0]
    # 拿商品数据
    goods = MainShow.objects.all()
    data = {
        'title': '首页',
        'swipers': swipers,
        'navs': navs,
        'must_bys': mustbys,
        'shop_img': shop_img,
        'shop_two': shops[1:3],
        'shop_more': shops[3:7],
        'shop_last': shops[7:],
        'goods': goods
    }
    return render(req, 'home/home.html', data)

def market(req, type_id, sub_type_id, sort_type):
    # 拿全部的分类数据
    all_types = GoodsType.objects.all()
    sort_type = int(sort_type)

    # 拿商品
    goods = Goods.objects.filter(categoryid=type_id)
    # 如果二级分类的id不得0 那就需要在原有数据集goods的基础上 找对应二级分类对应的数据
    if int(sub_type_id) != 0:
        goods = goods.filter(childcid=sub_type_id)

    # 一定是先拿数据 再排序策略
    if sort_type == DEFAULT_SORT:
        pass
        #一些套路
    elif sort_type == PRICE_SORT:
        goods = goods.order_by("price")
    else:
        goods = goods.order_by("-productnum")

    # t通过查询出来的数据集找到选中的那个分类数据
    select_type = all_types.get(typeid=type_id)

    # 拿到二级分类数据
    all_sub_type = select_type.childtypenames
    type_name_id_list = all_sub_type.split("#") #将子分类数据切分
    # 低端写法
    # sub_types = []
    # for i in type_name_id_list:
    #     name_ids = i.split(":")
    #     sub_types.append(name_ids)
    sub_types = [ i.split(':') for i in type_name_id_list]
    # print(sub_types)

    """
        0 表示综合排序
        1 表示价格最低
        2 表示销量优先
    """
    data = {
        'title': '闪购',
        'types': all_types,
        'goods': goods,
        'selected_typeid': type_id,
        'sub_types': sub_types,
        'select_sub_type_id': sub_type_id,
        'select_sort_type': str(sort_type)
    }
    return render(req, 'market/market.html', data)

@login_required(login_url="/axf/login")
def cart(req):
    # 获取用户
    user = req.user
    carts = Cart.objects.filter(
        user=user
    )
    is_select_all = not Cart.objects.filter(
            user=user,
            is_select=False).exists()
    # 如果购物车内压根没有数据 那全选按钮就不选中
    if not carts.exists():
        is_select_all = False
    data = {
        'title': '购物车',
        'cart_items':carts,
        'u_name': user.username,
        'phone': user.phone,
        'address': user.address.name,
        'money_sum': get_cart_sum_money(user),
        'is_all_select': is_select_all
    }
    return render(req, 'cart/cart.html', data)

def mine(req):
    # 拿用户
    user = req.user
    # 初始化 默认值
    is_login = False
    user_name = ""
    u_icon = ""
    # 判断用户user 是不是MyUser的实例
    if isinstance(user, MyUser):
        # 如果判断通过说明是登录过
        is_login = True
        user_name = user.username
        # 拼接用户头像 req.get_host() 拿到前端浏览器地址栏里输入域名加端口
        u_icon = "http://{host}/static/uploads/{icon_url}".format(
            host=req.get_host(),
            icon_url=user.icon.url
        )
    data = {
        'title': '我的',
        'is_login': is_login,
        'user_icon': u_icon,
        'user_name': user_name
    }
    return render(req, 'mine/mine.html', data)

def register_view(req):
    return render(req, 'user/register.html')

def my_login(req):
    return render(req, "user/login.html")


@login_required(login_url="/axf/login")
def order_api(req):
    user = req.user
    # 拿用户购物车内选中的商品的数据
    cart_items = Cart.objects.filter(
        user=user,
        is_select=True
    )
    # 创建订单
    order = Order.objects.create(
        user=user,
        status=0
    )
    sum_money = 0
    # 创建订单详情
    for i in cart_items:
        # 算单品的价格
        tmp_money = i.goods.price * i.num
        # 计算总价
        sum_money += tmp_money
        # 创建订单详情
        order_item = OrderItem.objects.create(
            order=order,
            item=i.goods,
            num=i.num,
            item_sum_money=tmp_money
        )
    # 记录本次订单的总价
    order.order_money = sum_money
    order.save()
    # 删除掉购物车内选中的商品
    cart_items.delete()
    return render(req, 'order/order.html', {"order": order})


def many_param(req):
    if req.method == "GET":
        return render(req, 'many_param.html')
    else:
        param = req.POST.get("my_data")
        print(param, type(param))
        loads_data = json.loads(param) #把json字符串转对应的数据结构
        print(loads_data, type(loads_data))
        return JsonResponse({"data": 'OK'})