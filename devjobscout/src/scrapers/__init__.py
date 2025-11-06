"""Scrapers para diferentes plataformas de empleo"""
from .linkedin_agent_v2 import LinkedInScraper
from .infojobs_agent import InfoJobsScraper
from .remoteok_agent import RemoteOKScraper

__all__ = ['LinkedInScraper', 'InfoJobsScraper', 'RemoteOKScraper']
