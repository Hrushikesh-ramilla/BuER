"""Structural address verification and house number comparator."""
import re
from typing import Optional, Tuple

_UNIT_PREFIX = re.compile(
    r'\b(?:suite|ste|apt|apartment|unit|fl|floor|bldg|building|shop|office|plot|block|room|rm|lot|dept|p\.?o\.?\s*box)\s*#?\s*[a-z0-9\-]+',
    re.IGNORECASE
)
_LEADING_HOUSE_NUM = re.compile(r'^(?:#\s*|(?:no|ndeg)\.?\s*)?(\d+)\b', re.IGNORECASE)


class StructuralAddressComparator:
    """Detects numeric conflicts in addresses to prevent false merges between distinct businesses."""

    @staticmethod
    def extract_clean_number(address: Optional[str]) -> Optional[str]:
        """Strip unit/suite numbers and isolate the primary street number."""
        if not address:
            return None
        stripped = _UNIT_PREFIX.sub(" ", address)
        m = _LEADING_HOUSE_NUM.search(stripped.strip())
        return m.group(1).lstrip("0") if m else None

    @classmethod
    def evaluate_number_compatibility(cls, addr1: Optional[str], addr2: Optional[str]) -> float:
        """Returns:
            1.0 if numbers match exactly
            0.0 if both have distinct, conflicting street numbers (hard decoy veto)
            0.5 if either number is absent or unverifiable
        """
        n1 = cls.extract_clean_number(addr1)
        n2 = cls.extract_clean_number(addr2)
        
        if n1 is None or n2 is None:
            return 0.5
        
        if n1 == n2:
            return 1.0
            
        return 0.0
