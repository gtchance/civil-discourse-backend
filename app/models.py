# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class School(models.Model):
    name = models.CharField(max_length=100)
    email_domain = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=50)
    body = models.TextField()
    pub_date = models.DateTimeField('date published')
    poster = models.ForeignKey(User)
    school = models.ForeignKey(School)

    def __str__(self):
        return self.title


class Comment(models.Model):
    commenter = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    body = models.TextField()
    pub_date = models.DateTimeField('date published')


    def __str__(self):  # __unicode__ on Python 2
        return self.post.title + "-" + self.commenter.username + "-" + str(self.pub_date)
