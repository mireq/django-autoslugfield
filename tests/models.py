# -*- coding: utf-8 -*-
from django.db import models
from django_autoslugfield import AutoSlugField


class ModelBase(models.Model):
	title = models.CharField(max_length=10)

	def __str__(self):
		return self.title

	class Meta:
		abstract = True


class Category(models.Model):
	name = models.CharField(max_length=10)

	def __str__(self):
		return self.name


class SimpleModel(ModelBase):
	slug = AutoSlugField(max_length=10, unique=True)


class CustomTitleModel(ModelBase):
	slug = AutoSlugField(max_length=10, unique=True, title_field='custom')
	custom = models.CharField(max_length=10)


class RespectToPkModel(ModelBase):
	slug = AutoSlugField(max_length=10, in_respect_to=('pk',))


class RespectToUniqueTogether(ModelBase):
	slug = AutoSlugField(max_length=10, in_respect_to=('a', 'b'))
	a = models.CharField(max_length=10)
	b = models.CharField(max_length=10)

	class Meta:
		unique_together = [('a', 'b')]


class RespectToParentModel(ModelBase):
	parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
	slug = AutoSlugField(max_length=10, in_respect_to=('parent__slug',))


class CustomReserveModel(ModelBase):
	slug = AutoSlugField(max_length=10, reserve_chars=2, unique=True)
