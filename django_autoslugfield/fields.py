# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import signals, SlugField

from .utils import unique_slugify


class AutoSlugField(SlugField):
	def __init__(self, reserve_chars=5, title_field=None, filter_fields=(), *args, **kwargs):
		super(AutoSlugField, self).__init__(*args, **kwargs)
		self.reserve_chars = reserve_chars
		self.title_field = title_field
		self.filter_fields = filter_fields

	def contribute_to_class(self, cls, name, virtual_only=False):
		signals.pre_save.connect(self.unique_slugify, sender=cls)
		super(AutoSlugField, self).contribute_to_class(cls, name, virtual_only)

	def unique_slugify(self, instance, **kwargs): #pylint: disable=unused-argument
		return unique_slugify(instance, self.name, self.reserve_chars, self.title_field, self.filter_fields)
