# -*- coding: utf-8 -*-
import re

from django.db import models
from django.db.models import F, Value as V, Case, When, Q
from django.db.models.constants import LOOKUP_SEP
from django.db.models.expressions import Window
from django.db.models.functions import Length, RowNumber, Concat, Cast
from django.utils.encoding import force_str
from django.utils.text import slugify


EMPTY_SLUG = '-'
SEPARATOR = '-'

ESCAPE_REGEX = re.compile(r'([.\\+*^?$!=|:\[\](){}<>-])')


def regex_escape(text):
	"""
	This function escapes lesss chars, it's used to query database, which don't
	support all escape sequencies.
	"""
	text = ESCAPE_REGEX.sub(r'\\\1', text)
	text = text.replace('\000', '\\000')
	return text


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

	# get queryset
	model = instance.__class__
	queryset = model._default_manager.all()

	# preserve saved slug
	if instance.pk and queryset.filter(**{slug_field_name: slug, 'pk': instance.pk}):
		return slug

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
	if is_unique(model, in_respect_to):
		setattr(instance, slug_field_name, slug)
		return slug

	# construct regex query
	slug_regex = f'^{regex_escape(slug)}({regex_escape(SEPARATOR)}[0-9]+)?$'
	slug_field_query = slug_field_name + '__regex'

	# construct in_respect_to filters
	in_respect_to = {f: get_instance_attribute(instance, f) for f in in_respect_to}
	in_respect_to[slug_field_query] = slug_regex

	# search for gaps (filter is not possible with window functions)
	all_slugs = (queryset
		.filter(**in_respect_to)
		.exclude(**{slug_field_name: f'{slug}-1'})
		.annotate(row_number_=Window(
			expression=RowNumber(),
			order_by=[Length(slug_field_name), slug_field_name]
		))
		.annotate(expected_slug_=Case(
				When(Q(row_number_=1), then=V(slug)),
				default=Concat(
					V(slug),
					V(SEPARATOR),
					Cast(F('row_number_'), models.CharField(max_length=255))
				)
			)
		)
		.annotate(is_slug_gap=Case(
			When(Q(**{slug_field_name: F('expected_slug_')}), then=V(False)),
			default=V(True)
		))
		.values_list('expected_slug_', 'row_number_', 'is_slug_gap')
	)

	# search gap
	new_slug = None
	last_row_number = None
	for new_slug, last_row_number, is_gap in all_slugs.iterator():
		if is_gap:
			break
	else:
		if last_row_number is not None:
			last_row_number += 1
			new_slug = f'{slug}-{last_row_number}'
	if new_slug is None:
		new_slug = slug

	setattr(instance, slug_field_name, new_slug)
	return new_slug
