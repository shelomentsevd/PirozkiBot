import re
from datetime import datetime

"""
	Common functions
"""

def iso8601(utc):
	"""
		From UTC to iso8601
	"""
	return datetime.fromtimestamp(utc).isoformat()

def br(text):
	"""
		Replace <br> to '\n'
	"""
	result = re.sub('\s*<br>\s*', '\n', text)
	return result

def author(raw_text):
	"""
		Makes author nick pretty
	"""
	result = re.sub('\[id[0-9^\|]+\||[\]]', '', raw_text).replace('&amp;', '&').strip()
	return re.sub(' +', ' ', result)