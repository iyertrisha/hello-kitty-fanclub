"""
Noticeboard service module
"""
from .noticeboard_service import (
    get_active_notices,
    create_notice,
    format_notices_for_display
)

__all__ = [
    'get_active_notices',
    'create_notice',
    'format_notices_for_display'
]

