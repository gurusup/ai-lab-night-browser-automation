"""Extractores de información"""
from .stack_extractor import StackExtractor
from .cv_parser import CVParser, extract_stack_from_cv
from .github_extractor import GitHubExtractor, extract_github_profile

__all__ = ['StackExtractor', 'CVParser', 'extract_stack_from_cv', 'GitHubExtractor', 'extract_github_profile']
