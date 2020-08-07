import io

from django.core.mail import send_mail
from qrcode import ERROR_CORRECT_H
from rest_framework.views import *
from rest_framework.response import Response
from django.http import HttpResponse
from .sers import *
from shiyanlou.settings import SECRET_KEY
from celery_email.send_email import connect_redis
from celery_email.send_email import sendemail
import re
import datetime
import jwt
import requests
import uuid
import qrcode



# 注册发送邮件验证码
class Verify_code(APIView):
    def post(self, request):
        email = request.data.get('email')
        print(email)
        if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            sendemail.delay(email)
            return Response({'code': 200, 'msg': '邮件已发送'})
        else:
            return Response({'code': 401, 'msg': '邮箱格式不正确'})

# 注册
class Register(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        verify_code = request.data.get('verify_code')
        print(email,password)
        '''
        	检测验证码是否过期：用于登录或者前端验证使用
        	'''
        rd = connect_redis()
        vcode = rd.get('code')
        if not vcode:
            return Response({'code': 402, 'msg': '验证码失效，请重新获取！！'})
        user = User.objects.filter(email=email, password=password).first()
        if user:
            return Response({'code': 405, 'msg': '用户已存在请直接登录！！'})
        if vcode == verify_code:
            data = {
                'email': email,
                'password': password
            }
            ser = UserSerializer(data=data)
            if ser.is_valid():
                ser.save()
                return Response({'code': 200, 'msg': '注册成功'})
            else:
                return Response({'code': 403, 'msg': ser.errors})

# 登录
class Login(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()
        if user:
            if password == user.password:
                payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # 有效期时间
                    'data': {  # 用户信息
                        'uid': user.id,
                        'username': user.email
                    }
                }
                token = jwt.encode(payload=payload, key=SECRET_KEY)
                return Response({'code': 200, 'msg': '登录成功', 'token': token,'id':user.id})
            else:
                return Response({'code': 400, 'msg': '密码错误，请重新输入！！！'})
        else:
            return Response({'code': 403, 'msg': '登录失败'})

# 微博第三方登录
class WeiboView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        data = {
            'client_id': '2028331105',
            'client_secret': '9d0835ec4c6ffc399b5892ea54d5c141',
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'http://127.0.0.1:8080/weibo'
        }
        res = requests.post('https://api.weibo.com/oauth2/access_token', data)
        uid = res.json()['uid']
        print(uid)
        if not uid:
            return Response({'code': 406, 'msg': '微博登录失败'})
        # access_token = res.json()['access_token']
        user = ThirdPartyLogin.objects.filter(uid=uid).first()
        if not user:
            ThirdPartyLogin.objects.create(uid=uid, login_type=                                                        1)
            return Response({'code': 201, 'msg': '微博登录成功', 'uid': uid})
        return Response({'code': 202, 'msg': '登录成功'})

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        uid = request.data.get('uid')
        user = User.objects.filter(email=email, password=password).first()
        if user:
            User.objects.filter(id=user.id).update(is_active=1)
            ThirdPartyLogin.objects.filter(uid=uid).update(user=user.id)
            return Response({'code': 203, 'msg': '账号绑定成功'})
        else:
            return Response({'code': 408, 'msg': '该账号未注册，请先注册！！！'})

# 发送重置密码邮件
class Send_Email(APIView):
    def post(self, request):
        email = request.data.get('email')
        print(email)
        if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            user = User.objects.filter(email=email).first()
            if user:
                send_mail(
                    subject='实验楼重置密码邮件',
                    message='实验楼重置密码！！！',
                    from_email='15047061455@163.com',
                    recipient_list=[email],
                    html_message='<a href="http://127.0.0.1:8080/resetting_password?email={}">点击链接重置密码</a>'.format(email)
                )
                return Response({'coed': 200, 'msg': '重置密码邮件发送成功'})
            else:
                return Response({'code': 501, 'msg': '该用户不存在，请确认邮箱是否正确'})
        else:
            return Response({'code': 409, 'msg': '输入邮箱格式不正确'})

# 重置密码
class Resetting_Password(APIView):
    def post(self, request):
        passwd1 = request.data.get('passwd1')
        passwd2 = request.data.get('passwd2')
        email = request.data.get('email')
        if passwd1 == passwd2:
            User.objects.filter(email=email).update(password=passwd1)
            return Response({'code': 200, 'msg': '密码重置成功'})
        else:
            return Response({'code': 503, 'msg': '两次密码不一致'})


# 个人信息
class PIMView(APIView):
    def get(self, request):
        email = request.GET.get('email')
        query = User.objects.filter(email=email)
        ser = UserSerializer(query, many=True)
        return Response(ser.data)

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        img1 = request.FILES.get('img')
        img2 = img1.name
        img = 'static/pic/' + img2
        with open(img, 'wb') as f:
            data = img1.file.read()
            f.write(data)
        print(name, email, img)
        if all([name, email, img]):
            User.objects.filter(email=email).update(name=name, img=img)
            return Response({'code': 200, 'msg': '修改成功'})
        else:
            return Response({'code': 401, 'msg': '添加失败'})

# 生成邀请码
def invitecode(request):
    email = request.GET.get('email')
    icode = uuid.uuid1()
    User.objects.filter(email=email).update(invitation_code=icode)
    qr = qrcode.QRCode(version=20, error_correction=ERROR_CORRECT_H, box_size=3, border=2)
    qr.add_data('sky')
    qr.make()
    img = qr.make_image()
    buf = io.BytesIO()
    img.save(buf, 'jpeg')
    return HttpResponse(buf.getvalue(), 'image/jpeg')


# 课程展示
class ShowCourse(APIView):
    def get(self,request):
        tag_obj = Tag.objects.all()
        course_type = TagSerializer(tag_obj,many=True).data
        pay_obj = Member.objects.all()
        pay_type = MemberSerializer(pay_obj,many=True).data
        return Response({
            'code':200,
            'course_type':course_type,
            'pay_type':pay_type,
            'msg':'ok'
        })

class GetCourse(APIView):

    def get(self,request):
        course_obj = Course.objects.filter(online=1)
        course = CourseSerializer(course_obj,many=True).data
        return Response({
            'course':course
        })

    def post(self,request):
        lang_choice = request.data['lang_choice']
        if lang_choice == '':
            course_obj = Course.objects.all()
            course = CourseSerializer(course_obj, many=True).data
            return Response({
                'code':200,
                'course_list': course
            })

        else:
            course_obj = Course.objects.filter(tag=lang_choice)
            course_list = CourseSerializer(course_obj,many=True).data

            return Response({
                'code':200,
                'course_list':course_list
            })

class Follow(APIView):
    def post(self,request):
        id = request.data['cid']
        obj = Course.objects.get(id=id)
        obj.attention += 1
        obj.save()
        return Response({'msg':'关注成功'})

class Detail(APIView):
    def post(self,request):
        id = request.data['id']
        print(id)
        goods_obj = Course.objects.filter(id=id)
        goods_list = CourseSerializer(goods_obj,many=True).data

        return Response({
            'msg':'ok',
            'goodslist':goods_list
        })


class Add(APIView):
    def post(self,request):
        print('提交')
        data = request.data
        print(data)
        obj = CourseSerializer(data=data)
        if obj.is_valid():
            print('提交成功')
            resp = {'msg':'提交成功','code':200}
            obj.save()
        else:
            print(obj.errors)
            resp = {'msg':'提交失败','code':201}
        return Response(resp)

class Del(APIView):
    def post(self,request):
        id = request.data['id']
        obj = Course.objects.filter(id=id).delete()
        return Response({'msg':'删除成功'})