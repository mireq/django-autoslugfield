# -*- coding: utf-8 -*-
from django.db.models.constants import LOOKUP_SEP
from django.utils.encoding import force_str
from django.utils.text import slugify


EMPTY_SLUG = '-'
SEPARATOR = '-'


def get_title(instance, title_field=None):
	"""
	Returns title for instance
	"""
	if title_field:
		return force_str(getattr(instance, title_field))
	else:
		return force_str(instance)


def get_instance_attribute(instance, attribute):
	lookups = attribute.split(LOOKUP_SEP)
	attribute = instance
	for lookup in lookups:
		attribute = getattr(attribute, lookup, None)
		if attribute is None:
			break
	return attribute


def is_unique(model, in_respect_to):
	if not in_respect_to:
		return False

	# collect unique
	unique = []
	for field in model._meta.get_fields():
		if getattr(field, 'unique', False):
			unique.append(set([field.name]))
	for combination in model._meta.unique_together:
		unique.append(set(combination))

	in_respect_to = set(in_respect_to)

	# if in_respect_to contains all unique checks, key is unique
	for unique_check in unique:
		if not (unique_check - in_respect_to):
			return True

	return False


def unique_slugify(instance, slug_field_name, reserve_chars=5, title_field=None, in_respect_to=()):
	# get current slug
	slug = getattr(instance, slug_field_name)

	# if there is not slug, generate new
	if not slug:
		slug = slugify(get_title(instance, title_field))

	# for empty slug, set just empty dash
	if not slug:
		slug = '-'

	# trim slug to max length - reserved chars
	slug_field = instance._meta.get_field(slug_field_name)
	slug_length = slug_field.max_length
	slug = slug[:slug_length - reserve_chars]

	# if in_respect_to is unique, don't need to generate unique slug
	model = instance.__class__
	if is_unique(model, in_respect_to):
		setattr(instance, slug_field_name, slug)
		return slug

	# exclude current model
	queryset = model._default_manager.all()
	if instance.pk:
		queryset = queryset.exclude(pk=instance.pk)

	slug_field_query = slug_field_name + '__startswith'

	in_respect_to = {f: get_instance_attribute(instance, f) for f in in_respect_to}
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
