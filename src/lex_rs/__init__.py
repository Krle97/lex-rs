# src/lex_rs/__init__.py
from .parser import parse
from .models import Article, Paragraph, Point

__version__ = "0.1.0"
__all__ = ['parse', 'Article', 'Paragraph', 'Point']