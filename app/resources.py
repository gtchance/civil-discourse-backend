from tastypie import utils, fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from django.contrib.auth.models import User
from tastypie.http import HttpUnauthorized, HttpForbidden
from django.contrib.auth import authenticate, login, logout
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import ApiKeyAuthentication, BasicAuthentication, Authentication
from django.db import IntegrityError
from tastypie.exceptions import BadRequest
from tastypie.utils import trailing_slash
from django.conf.urls import url
from app.models import Post, School, Comment
from tastypie.models import ApiKey


def createAPIKey(user):
    return ApiKey.objects.get_or_create(user=user)[0].key


class UserResource(ModelResource):
    posts = fields.ToManyField('app.resources.PostResource', 'post_set', related_name='poster')

    class Meta:
        queryset = User.objects.all()
        resource_name = 'auth/user'
        excludes = ['email', 'password', 'is_superuser']
        allowed_methods = ['post']
        filtering = {
            'school': ALL_WITH_RELATIONS,
            'date': ALL
        }
        authentication = Authentication()
        authorization = Authorization()

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login")
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))

        # username is the same as email
        email = data.get('username', '')
        password = data.get('password', '')

        user = authenticate(username=email, password=password)

        if user:
            token = createAPIKey(user)
            school_domain = email.split('@')[1]
            school = list(School.objects.filter(email_domain=school_domain))[0].id
            return self.create_response(request, {
                'error': False,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'token': token,
                'school': school,
                'id': user.id
            })
        else:
            return self.create_response(request, {
                'error': True,
                'message': 'Unable to authenticate with provided credentials.',
            }, HttpUnauthorized)


class UserSignUpResource(ModelResource):
    class Meta:
        object_class = User
        resource_name = 'auth/register'
        fields = ['username', 'first_name', 'last_name', 'email']
        allowed_methods = ['post']
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        queryset = User.objects.all()

    def obj_create(self, bundle, request=None, **kwargs):
        email = bundle.data.get('email')
        split_email = email.split('@')
        if len(split_email) < 2:
            raise BadRequest('Email must be a valid school email address.')

        school_domain = split_email[1]
        school_exists = False
        for school in School.objects.all():
            if school.email_domain == school_domain:
                school_exists = True
                break

        if not school_exists:
            raise BadRequest('This school is not registered in the database.')

        try:
            bundle.data['username'] = email
            bundle = super(UserSignUpResource, self).obj_create(bundle, request=request, **kwargs)
            bundle.obj.set_password(bundle.data.get('password'))
            bundle.obj.save()
        except IntegrityError:
            raise BadRequest('That username or email already exists')
        return bundle


class PostResource(ModelResource):
    poster = fields.ToOneField(UserResource, 'poster')
    school = fields.ToOneField('app.resources.SchoolResource', 'school')
    comments = fields.ToManyField('app.resources.CommentResource', 'comment_set', related_name='post')

    class Meta:
        queryset = Post.objects.all()
        resource_name = 'post'
        excludes = []
        allowed_methods = ['get', 'post']
        filtering = {
            'school': ALL_WITH_RELATIONS,
            'date': ALL
        }
        ordering = ['date']

        # FIXME: Don't allow all access!
        authorization = Authorization()
        authentication = ApiKeyAuthentication()


class SchoolResource(ModelResource):
    posts = fields.ToManyField(PostResource, 'post_set', related_name='school')

    class Meta:
        queryset = School.objects.all()
        resource_name = 'school'
        excludes = []
        allowed_methods = ['get']
        # FIXME: Don't allow all access!
        authorization = Authorization()
        authentication = ApiKeyAuthentication()


class CommentResource(ModelResource):
    post = fields.ToOneField(PostResource, 'post')
    commenter = fields.ToOneField(UserResource, 'commenter', full=True)

    class Meta:
        queryset = Comment.objects.all()
        resource_name = 'comment'
        excludes = []
        allowed_methods = ['get', 'post']
        filtering = {
            'post': ALL_WITH_RELATIONS,
            'date': ALL
        }
        ordering = ['date']
        # FIXME: Don't allow all access!
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
