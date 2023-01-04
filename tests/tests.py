# -*- coding: utf-8 -*-
from django.test import TestCase

from .models import SimpleModel, CustomTitleModel, RespectToPkModel, RespectToParentModel, RespectToUniqueTogether, CustomReserveModel
from django_autoslugfield.utils import EMPTY_SLUG, SEPARATOR, regex_escape


class TestField(TestCase):
	def test_simple_regex(self):
		chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[]^_`{|}~ \t\n\r\x0b\x0c\x00\\'
		self.assertEqual('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\\!"#\\$%&\'\\(\\)\\*\\+,\\-\\./\\:;\\<\\=\\>\\?@\\[\\]\\^_`\\{\\|\\}~ \t\n\r\x0b\x0c\\000\\\\', regex_escape(chars))

	def test_simple(self):
		# first instance
		instance = SimpleModel.objects.create(title='Title')
		self.assertEqual('title', instance.slug)

		# duplicate
		instance = SimpleModel.objects.create(title='Title')
		self.assertEqual(f'title{SEPARATOR}2', instance.slug)

	def test_long(self):
		# Trimmed to 5 characters
		instance = SimpleModel.objects.create(title='0123456789')
		self.assertEqual('01234', instance.slug)

		# duplicate
		instance = SimpleModel.objects.create(title='0123456789')
		self.assertEqual(f'01234{SEPARATOR}2', instance.slug)
		instance = SimpleModel.objects.create(title='01234')
		self.assertEqual(f'01234{SEPARATOR}3', instance.slug)

	def test_empty_slug(self):
		instance = SimpleModel.objects.create(title='')
		self.assertEqual(EMPTY_SLUG, instance.slug)

	def test_filled_slug(self):
		instance = SimpleModel.objects.create(title='title', slug='slug')
		self.assertEqual('slug', instance.slug)

	def test_custom_title(self):
		instance = CustomTitleModel.objects.create(title='title', custom='cust')
		self.assertEqual('cust', instance.slug)

	def test_respect_to_pk(self):
		instance = RespectToPkModel.objects.create(title='title')
		self.assertEqual('title', instance.slug)
		# no duplicate
		instance = RespectToPkModel.objects.create(title='title')
		self.assertEqual('title', instance.slug)

	def test_respect_to_parent(self):
		p = RespectToParentModel.objects.create(title='p')
		self.assertEqual('p', p.slug)
		child = RespectToParentModel.objects.create(title='p', parent=p)
		self.assertEqual('p', child.slug)
		child = RespectToParentModel.objects.create(title='p', parent=p)
		self.assertEqual(f'p{SEPARATOR}2', child.slug)

	def test_respect_to_unique_together(self):
		# a and b are unique
		instance = RespectToUniqueTogether.objects.create(title='title', a='', b='')
		self.assertEqual('title', instance.slug)

		# don't causes collision
		instance = RespectToUniqueTogether.objects.create(title='title', a='1', b='')
		self.assertEqual('title', instance.slug)
		instance = RespectToUniqueTogether.objects.create(title='title', a='', b='1')
		self.assertEqual('title', instance.slug)

	def test_find_gap(self):
		instances = [
			SimpleModel(title='s', slug='s'),
			SimpleModel(title='s', slug='s-2'),
			SimpleModel(title='s', slug='s-111'),
			SimpleModel(title='s', slug='s-3'),
			SimpleModel(title='s', slug='s-5'),
		]
		SimpleModel.objects.bulk_create(instances)
		instance = SimpleModel.objects.create(title='s')
		self.assertEqual('s-4', instance.slug)
		instance = SimpleModel.objects.create(title='s')
		self.assertEqual('s-6', instance.slug)

	def test_save_existing(self):
		instance = SimpleModel.objects.create(title='title')
		instance.save()
		self.assertEqual('title', instance.slug)

	def test_custom_reserve(self):
		instance = CustomReserveModel.objects.create(title='0123456789')
		self.assertEqual('01234567', instance.slug)

	def test_existing_1_prefix(self):
		instances = [
			SimpleModel(title='s', slug='s'),
			SimpleModel(title='s', slug='s-1'),
			SimpleModel(title='s', slug='s-2'),
		]
		SimpleModel.objects.bulk_create(instances)
		instance = SimpleModel.objects.create(title='s')
		self.assertEqual('s-3', instance.slug)
