# -*- coding: utf-8 -*-
from django.db.models import signals, SlugField

from .utils import unique_slugify


class AutoSlugField(SlugField):
	def __init__(self, reserve_chars=5, title_field=None, in_respect_to=(), *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.reserve_chars = reserve_chars
		self.title_field = title_field
		self.in_respect_to = in_respect_to

	def contribute_to_class(self, cls, name, virtual_only=False):
		signals.pre_save.connect(self.unique_slugify, sender=cls)
		super().contribute_to_class(cls, name, virtual_only)

	def unique_slugify(self, instance, **kwargs): #pylint: disable=unused-argument
		return unique_slugify(instance, self.name, self.reserve_chars, self.title_field, self.in_respect_to)

	def deconstruct(self):
		name, path, args, kwargs = super().deconstruct()
		kwargs['title_field'] = self.title_field
		if self.reserve_chars != 5:
			kwargs['reserve_chars'] = self.reserve_chars
		if self.in_respect_to:
			kwargs['in_respect_to'] = self.in_respect_to
		return name, path, args, kwargs
