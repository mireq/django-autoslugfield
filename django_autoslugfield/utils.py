# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import force_text
from django.utils.text import slugify


def get_title(instance, title_field=None):
	if title_field:
		return force_text(getattr(instance, title_field))
	else:
		return force_text(instance)


def unique_slugify(instance, slug_field_name, reserve_chars=5, title_field=None, in_respect_to=()):
	slug = getattr(instance, slug_field_name)
	if not slug:
		slug = slugify(get_title(instance, title_field))

	if not slug:
		slug = '-'

	slug_field = instance._meta.get_field(slug_field_name)
	slug_length = slug_field.max_length
	slug = slug[:slug_length - reserve_chars]

	queryset = instance.__class__._default_manager.all()
	if instance.pk:
		queryset = queryset.exclude(pk=instance.pk)
	slug_field_query = slug_field_name + '__startswith'

	in_respect_to = {f: getattr(instance, f) for f in in_respect_to}
	in_respect_to[slug_field_query] = slug

	all_slugs = set(queryset.filter(**in_respect_to).values_list(slug_field_name, flat=True))
	max_val = 10 ** (reserve_chars - 1) - 1
	setattr(instance, slug_field_name, create_unique_slug(slug, all_slugs, max_val))


def create_unique_slug(slug, all_slugs, max_val):
	unique_slug = slug
	suffix = 2
	while unique_slug in all_slugs:
		unique_slug = '%s-%d' % (slug, suffix)
		suffix += 1
		if suffix > max_val:
			break
	return unique_slug
