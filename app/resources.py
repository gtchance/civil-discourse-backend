from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from django.contrib.auth.models import User
from tastypie.http import HttpUnauthorized
from django.contrib.auth import authenticate
from tastypie.authorization import Authorization
from tastypie.authentication import ApiKeyAuthentication, Authentication
from django.db import IntegrityError
from tastypie.exceptions import BadRequest
from tastypie.utils import trailing_slash
from django.conf.urls import url
from app.models import Post, School, Comment
from tastypie.models import ApiKey


def createAPIKey(user):
    """

    :param user: The user to create a key for
    :type user: User model
    :return: The generated key
    :rtype: String
    """
    return ApiKey.objects.get_or_create(user=user)[0].key


class UserResource(ModelResource):
    """
    This class models a resource for the user model, including authentication
    """

    # The posts relating to the the user
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

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login")
        ]

    def login(self, request, **kwargs):
        """
        Handles log in requests
        """

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

            # create the response json
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
    """
    This class models a resource for the user model, but only relating to account creation
    """

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
            password = bundle.data.get('password')
            if len(password) < 6:
                raise BadRequest('Password must be at least 6 characters.')
            bundle.data['username'] = email
            bundle = super(UserSignUpResource, self).obj_create(bundle, request=request, **kwargs)

            bundle.obj.set_password(password)
            bundle.obj.save()
        except IntegrityError:
            raise BadRequest('That username or email already exists')
        return bundle


class PostResource(ModelResource):
    """
    This class models a resource for the post model
    """

    # The creator of the post
    poster = fields.ToOneField(UserResource, 'poster', full=True)

    # The school the post belongs to
    school = fields.ToOneField('app.resources.SchoolResource', 'school')

    # The comments belonging to the post
    comments = fields.ToManyField('app.resources.CommentResource', 'comment_set', related_name='post')

    class Meta:
        queryset = Post.objects.all()
        resource_name = 'post'
        excludes = []
        allowed_methods = ['get', 'post', 'delete']
        filtering = {
            'school': ALL_WITH_RELATIONS,
            'date': ALL
        }
        ordering = ['date']

        authorization = Authorization()
        authentication = ApiKeyAuthentication()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_search'), name="api_get_search"),
        ]


class SchoolResource(ModelResource):
    """
    This class models a resource for the school model
    """

    # Posts belonging to the school
    posts = fields.ToManyField(PostResource, 'post_set', related_name='school')

    class Meta:
        queryset = School.objects.all()
        resource_name = 'school'
        excludes = []
        allowed_methods = ['get']
        authorization = Authorization()
        authentication = ApiKeyAuthentication()


class CommentResource(ModelResource):
    """
    This class models a resource for the comment model
    """

    # posts relating to the comment
    post = fields.ToOneField(PostResource, 'post')

    # The creator of the comment
    commenter = fields.ToOneField(UserResource, 'commenter', full=True)

    class Meta:
        queryset = Comment.objects.all()
        resource_name = 'comment'
        excludes = []
        allowed_methods = ['get', 'post', 'delete']
        filtering = {
            'post': ALL_WITH_RELATIONS,
            'date': ALL
        }
        ordering = ['date']
        authorization = Authorization()
        authentication = ApiKeyAuthentication()
