from django.db import models

# Create your models here.

# 登录表
class User(models.Model):
    actives = ((0, '是否激活'), (1, '已激活'), (2, '未激活'))
    levels = ((0, '普通用户'), (1, '会员'), (2, 'VIP会员'))
    password = models.CharField(max_length=200, verbose_name='密码')
    email = models.EmailField()
    name = models.CharField(max_length=200, verbose_name='昵称', null=True)
    img = models.ImageField(upload_to='static/pic', null=True)
    is_active = models.SmallIntegerField(choices=actives, default=0)
    level = models.SmallIntegerField(choices=levels, default=0)
    integer = models.IntegerField(default=0)
    invitation_code = models.CharField(max_length=200, verbose_name='邀请码', null=True)

    class Meta:
        db_table = 'user'

# 第三方登录表
class ThirdPartyLogin(models.Model):
    type = ((1, '微博'), (2, '支付宝'))
    user = models.IntegerField(null=True)
    login_type = models.SmallIntegerField(choices=type, null=True)
    uid = models.CharField(max_length=200, verbose_name='微博号唯一的id')

    class Meta:
        db_table = 'thirdpartylogin'



# 课程表
class Course(models.Model):
    ONLINE = ((0,'未上线'),(1,'上线'))
    MEMBER = ((0,'非会员'),(1,'会员'),(2,'训练营'))
    title = models.CharField(max_length=255,verbose_name='标题',null=True)
    price = models.IntegerField(default=0)
    picture = models.ImageField(upload_to='static/pic',null=True,verbose_name='图片')
    info = models.CharField(max_length=255,verbose_name='简介',null=True)
    online = models.SmallIntegerField(choices=ONLINE,default=0)
    member = models.SmallIntegerField(choices=MEMBER,default=0)
    attention = models.IntegerField(null=True,verbose_name='关注量')
    learn = models.IntegerField(null=True,verbose_name='学过人数')
    teacher = models.ForeignKey('Teacher',on_delete=models.CASCADE,null=True)
    comment_num = models.IntegerField(null=True,verbose_name='评论数')
    path = models.ForeignKey('Path',on_delete=models.CASCADE,null=True)
    tag = models.ForeignKey('Tag',on_delete=models.CASCADE,null=True)
    recommand = models.CharField(null=True,max_length=255,verbose_name='推荐课程')
    detail = models.CharField(max_length=255,null=True,verbose_name='课程详情')
    section_num = models.IntegerField(null=True,verbose_name='章节数')

    class Meta:
        db_table = 'course'


# 类别表
class Member(models.Model):
    member = models.CharField(max_length=255,null=True)
    class Meta:
        db_table = 'member'


# 学习记录表
class User_course(models.Model):
    STATUS = ((0,'未完成'),(1,'完成'))
    course = models.ForeignKey('Course',on_delete=models.CASCADE,null=True)
    user = models.ForeignKey('User',on_delete=models.CASCADE,null=True)
    section = models.ForeignKey('Section',on_delete=models.CASCADE,null=True)
    status = models.IntegerField(choices=STATUS,default=0)
    class Meta:
        db_table = 'user_course'


# 老师表
class Teacher(models.Model):
    name = models.CharField(max_length=255)
    class Meta:
        db_table = 'Teacher'

# 课程标签
class Tag(models.Model):
    name = models.CharField(max_length=255,null=True)
    class Meta:
        db_table = 'Tag'

# 阶段表
class Path(models.Model):
    name = models.CharField(max_length=255)
    class Meta:
        db_table = 'Path'

# 课程章节表
class Section(models.Model):
    course = models.ForeignKey('Course',on_delete=models.CASCADE,null=True)
    section = models.CharField(max_length=255,null=True)
    video = models.CharField(max_length=255,null=True)
    sort = models.IntegerField(null=True)
    class Meta:
        db_table = 'Section'

# 评论表
class Comment(models.Model):
    STATUS = ((0,'否'),(1,'是'))
    content = models.TextField(null=True)
    pid = models.ForeignKey('self',on_delete=models.CASCADE,null=True,default=0,verbose_name='上级评论',related_name='上级评论')
    top = models.ForeignKey('self',on_delete=models.CASCADE,null=True,default=0,verbose_name='顶级评论',related_name='顶级评论')
    type = models.ForeignKey('self',on_delete=models.CASCADE,null=True,default=0,verbose_name='自身级别',related_name='自身级别')
    user = models.ForeignKey('User',on_delete=models.CASCADE,null=True)
    course = models.ForeignKey('Course',on_delete=models.CASCADE,null=True)
    comment_type = models.CharField(max_length=255,null=True,verbose_name='评论类型')
    status = models.SmallIntegerField(choices=STATUS,default=0)
    reason = models.CharField(max_length=255,null=True,verbose_name='失败原因')
    class Meta:
        db_table = 'Comment'


# 实验报告表
class Report(models.Model):
    section = models.ForeignKey('Section',on_delete=models.CASCADE,null=True)
    user = models.ForeignKey('User',on_delete=models.CASCADE,null=True)
    report_content =models.CharField(max_length=255,verbose_name='报告内容')
    report_title =models.CharField(max_length=255,verbose_name='报告标题')
    report_browse =models.CharField(max_length=255,verbose_name='报告浏览量')
    linknum = models.IntegerField(null=True,verbose_name='点赞数量')
    course = models.ForeignKey('Course',on_delete=models.CASCADE,null=True)
    class Meta:
        db_table = 'report'


# 实验问答表
class Answer(models.Model):
    course = models.ForeignKey('Course',on_delete=models.CASCADE,null=True)
    answer_content = models.CharField(max_length=255,null=True,verbose_name='问题内容')
    answer_title = models.CharField(max_length=255,null=True,verbose_name='问题标题')
    browse = models.IntegerField(null=True,verbose_name='浏览量')
    user = models.ForeignKey('User',on_delete=models.CASCADE,null=True)
    pid = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=0, verbose_name='上级评论',
                            related_name='上级评论')
    top = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=0, verbose_name='顶级评论',
                            related_name='顶级评论')
    type = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=0, verbose_name='自身级别',
                             related_name='自身级别')
    class Meta:
        db_table = 'answer'

# 用户和收藏实验问答报告表
class Collect(models.Model):
    TYPE = ((0,'实验报告'),(1,'实验问答'))
    user = models.ForeignKey('User',on_delete=models.CASCADE,null=True)
    find = models.ForeignKey('Answer',on_delete=models.CASCADE,null=True,verbose_name='实验报告/问答',related_name='实验报告')
    collect_type = models.SmallIntegerField(choices=TYPE,default=0)
    class Meta:
        db_table = 'collect'

# 订单记录表
class Order(models.Model):
    WAY = ((0,'未使用优惠'),(1,'使用积分'),(2,'使用优惠券'))
    USE = ((0,'未使用'),(1,'使用'))
    STATUS = ((0,'未完成'),(1,'完成'))
    PAY = ((0,'未支付'),(1,'已支付'))
    order_number = models.CharField(max_length=255,verbose_name='订单编号')
    user = models.ForeignKey('User',on_delete=models.CASCADE,null=True)
    course = models.ForeignKey('Course',on_delete=models.CASCADE,null=True)
    pay_type = models.CharField(max_length=255,verbose_name='支付方式')
    price = models.DecimalField(default=0,max_digits=7,decimal_places=2)
    price_pay = models.DecimalField(default=0,verbose_name='实际支付',max_digits=7,decimal_places=2)
    preferential_way = models.SmallIntegerField(choices=WAY,default=0,verbose_name='优惠方式')
    preferential_mone = models.DecimalField(null=True,verbose_name='优惠金额',max_digits=7,decimal_places=2)
    use_type = models.SmallIntegerField(choices=USE,default=0)
    order_status = models.SmallIntegerField(choices=STATUS,default=0)
    code = models.CharField(max_length=255,null=True)
    coupon = models.CharField(max_length=255,null=True)
    pay_status = models.SmallIntegerField(choices=PAY,default=0)
    class Meta:
        db_table = 'order'