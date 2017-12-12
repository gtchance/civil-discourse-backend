# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class School(models.Model):
    """
    This class models a school object
    """

    # The name of the school
    name = models.CharField(max_length=100)

    # The email domain for emails created by the school, e.g. "colby.edu"
    email_domain = models.CharField(max_length=50)

    def __str__(self):
        """
        Returns a string describing the school
        """
        return self.name



class Post(models.Model):
    """
    This class models a post object
    """

    # The title of the post
    title = models.CharField(max_length=50)

    # The body text of the post
    body = models.TextField()

    # The date the post was published
    pub_date = models.DateTimeField('date published')

    # The creator of the post
    poster = models.ForeignKey(User)

    # The school the post belongs to
    school = models.ForeignKey(School)


    def __str__(self):
        """
        Returns a string describing the post
        """
        return self.title


class Comment(models.Model):
    """
    This class models a comment object
    """

    # The creator of the comment
    commenter = models.ForeignKey(User)

    # The post the comment belongs to
    post = models.ForeignKey(Post)

    # The body text of the comment
    body = models.TextField()

    # The date the comment was published
    pub_date = models.DateTimeField('date published')


    def __str__(self):
        """
        Returns a string describing the comment
        """
        return self.post.title + "-" + self.commenter.username + "-" + str(self.pub_date)
