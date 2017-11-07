# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import Post, Comment, School

admin.site.register(Post)
admin.site.register(School)
admin.site.register(Comment)