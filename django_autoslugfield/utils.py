# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def get_meta(instance):
	return getattr(instance, "_meta")


def get_default_manager(obj):
	if inspect.isclass(obj):
		return getattr(obj, "_default_manager")
	else:
		return getattr(obj.__class__, "_default_manager")


def unique_slugify(self, instance, slug_field, reserve_chars=5, title_field=None, filter_fields=()):
	slug = getattr(instance, slug_field)
	if not slug:
		if title_field:
			slug = slugify(getattr(instance, title_field))
		else:
			slug = slugify(smart_unicode(instance))

	if not slug:
		slug = '-'
	slug_field = get_meta(instance).get_field(slug_field)
	slug_length = slug_field.max_length
	slug = slug[:slug_length - reserve_chars]

	queryset = get_default_manager(instance).all()
	if instance.pk:
		queryset = queryset.exclude(pk = instance.pk)
	slug_field_query = slug_field + '__startswith'

	filter_fields = dict([(f, getattr(instance, f)) for f in filter_fields])
	filter_fields[slug_field_query] = slug

	all_slugs = set(queryset.filter(**filter_fields).values_list(slug_field, flat = True)) # pylint: disable=star-args
	max_val = 10 ** (reserve_chars - 1) - 1
	setattr(instance, slug_field, create_unique_slug(slug, all_slugs, max_val))


def create_unique_slug(slug, all_slugs, max_val):
	if not slug in all_slugs:
		return slug
	else:
		for suffix in xrange(2, max_val):
			new_slug = slug + '-' + str(suffix)
			if not new_slug in all_slugs:
				return new_slug
	return slug
