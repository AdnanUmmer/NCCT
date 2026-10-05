from pathlib import Path
from django.core.exceptions import ValidationError


def validate_pdf(file):
    if Path(file.name).suffix.lower() != '.pdf' or file.size > 20 * 1024 * 1024:
        raise ValidationError('Upload a PDF smaller than 20 MB.')
    position = file.tell()
    file.seek(0)
    header = file.read(5)
    file.seek(position)
    if header != b'%PDF-':
        raise ValidationError('This file is not a PDF.')
    content_type = getattr(file, 'content_type', None)
    if content_type and content_type not in ('application/pdf', 'application/octet-stream'):
        raise ValidationError('The upload must have a PDF content type.')


def validate_link(value):
    if not (value.startswith(('/', '#', 'https://', 'http://', 'mailto:', 'tel:')) and ' ' not in value):
        raise ValidationError('Use a site path such as /contact/, an #anchor, or a full https:// address.')


def validate_ga4(value):
    import re
    if not re.fullmatch(r'G-[A-Z0-9]{6,14}', value):
        raise ValidationError('A GA4 measurement ID looks like G-XXXXXXXXXX.')
