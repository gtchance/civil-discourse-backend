from tastypie import utils, fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from django.contrib.auth.models import User
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import ApiKeyAuthentication, BasicAuthentication
from app.models import Post, School, Comment

#TODO: limit interation based on authed user's school

class UserResource(ModelResource):

    posts = fields.ToManyField('app.resources.PostResource', 'post_set', related_name='poster')

    class Meta:
        queryset = User.objects.all()
        resource_name = 'auth/user'
        excludes = ['email', 'password', 'is_superuser']
        allowed_methods = ['get']
        filtering = {
            'school': ALL_WITH_RELATIONS,
            'date': ALL
        }
        authentication = BasicAuthentication()


class PostResource(ModelResource):

    poster = fields.ToOneField(UserResource, 'poster')
    school = fields.ToOneField('app.resources.SchoolResource', 'school')
    comments = fields.ToManyField('app.resources.CommentResource', 'comment_set', related_name='post')

    class Meta:
        queryset = Post.objects.all()
        resource_name = 'post'
        excludes = []
        allowed_methods = ['get']
        filtering = {
            'school': ALL_WITH_RELATIONS,
            'date': ALL
        }
        ordering = ['date']

        # FIXME: Don't allow all access!
        authorization = Authorization()


class SchoolResource(ModelResource):

    posts = fields.ToManyField(PostResource, 'post_set', related_name='school')

    class Meta:
        queryset = School.objects.all()
        resource_name = 'school'
        excludes = []
        allowed_methods = ['get']
        # FIXME: Don't allow all access!
        authorization = Authorization()


class CommentResource(ModelResource):

    post = fields.ToOneField(PostResource, 'post')

    class Meta:
        queryset = Comment.objects.all()
        resource_name = 'comment'
        excludes = []
        allowed_methods = ['get']
        filtering = {
            'post': ALL_WITH_RELATIONS,
            'date': ALL
        }
        ordering = ['date']
        # FIXME: Don't allow all access!
        authorization = Authorization()
