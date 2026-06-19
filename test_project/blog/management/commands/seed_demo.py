"""Populate the blog demo with realistic, generator-friendly sample data.

Counts are chosen on purpose so the generated admin shows off every
data-driven heuristic:

* ~150 posts (< the 250 ``date_hierarchy`` threshold) → ``date_hierarchy``.
* 120 tags (> the 100 ``raw_id`` threshold) → ``raw_id_fields`` for M2M/FKs.
* a handful of authors/categories (< 25) → ``list_filter``.
"""

import datetime
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from test_project.blog.models import Author, Comment, Post
from test_project.blog.taxonomy.models import Category, Tag

AUTHORS = ['Ada Lovelace', 'Grace Hopper', 'Alan Turing', 'Edsger Dijkstra']
CATEGORIES = [
    'Python',
    'Django',
    'Databases',
    'DevOps',
    'Security',
    'Testing',
    'Frontend',
    'Career',
]
ADJECTIVES = [
    'Practical',
    'Modern',
    'Hidden',
    'Fast',
    'Robust',
    'Elegant',
    'Painless',
    'Battle-tested',
    'Minimal',
    'Opinionated',
]
TOPICS = [
    'migrations',
    'type hints',
    'the ORM',
    'admin customization',
    'async views',
    'caching',
    'signals',
    'testing',
    'packaging',
    'CI',
]
COMMENTERS = ['reader42', 'pythonista', 'dev_jane', 'curious_cat', 'lurker']


class Command(BaseCommand):
    help = 'Populate the blog demo with realistic sample data.'

    def handle(self, *args, **options):
        random.seed(0)  # reproducible demo

        # Idempotent: wipe demo content, then recreate it.
        Comment.objects.all().delete()
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        Author.objects.all().delete()

        authors = [
            Author.objects.create(
                name=name,
                slug=slugify(name),
                bio=f'{name} writes about software and computing.',
            )
            for name in AUTHORS
        ]
        categories = [
            Category.objects.create(name=name, slug=slugify(name))
            for name in CATEGORIES
        ]
        # 120 tags > the 100 raw_id threshold.
        tags = [
            Tag.objects.create(name=f'tag-{i:03d}', slug=f'tag-{i:03d}')
            for i in range(120)
        ]

        today = datetime.date.today()
        for i in range(150):
            title = f'{random.choice(ADJECTIVES)} {random.choice(TOPICS)} #{i}'
            created = today - datetime.timedelta(days=i * 2)
            post = Post.objects.create(
                title=title,
                slug=f'{slugify(title)}-{i}',
                body=f'A demo post about {title.lower()}.\n\n' * 3,
                created_at=created,
                published_at=created + datetime.timedelta(days=2),
                is_published=(i % 5 != 0),
                author=random.choice(authors),
                category=random.choice(categories),
            )
            post.tags.set(random.sample(tags, k=random.randint(1, 3)))
            for _ in range(random.randint(0, 3)):
                Comment.objects.create(
                    author_name=random.choice(COMMENTERS),
                    body='Great post, thanks for sharing!',
                    post=post,
                    created_at=created
                    + datetime.timedelta(days=random.randint(1, 10)),
                )

        user_model = get_user_model()
        if not user_model.objects.filter(username='admin').exists():
            user_model.objects.create_superuser(
                'admin', 'admin@example.com', 'admin'
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded {len(authors)} authors, {len(categories)} '
                f'categories, {len(tags)} tags, {Post.objects.count()} '
                f'posts, {Comment.objects.count()} comments. '
                'Superuser: admin / admin.'
            )
        )
