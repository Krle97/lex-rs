# src/lex_rs/__init__.py
from .parser import parse
from .models import Law, Article, Paragraph, Point

__all__ = ['parse', 'Law', 'Article', 'Paragraph', 'Point']