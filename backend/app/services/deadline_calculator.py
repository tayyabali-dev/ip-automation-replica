"""
Deadline Calculator Service for USPTO Office Actions.

Calculates response deadlines with extension fees, accounting for
weekends and US federal holidays.
"""
import logging
from datetime import date, timedelta
from typing import List, Optional
from calendar import monthrange

from app.models.office_action import DeadlineTier, DeadlineCalculation

logger = logging.getLogger(__name__)


# US Federal Holidays (observed dates may shift for weekends)
# This is a simplified version - for production, consider using the `holidays` package
def get_us_federal_holidays(year: int) -> List[date]:
    """
    Returns a list of US federal holidays for the given year.
    Includes observed dates when holidays fall on weekends.
    """
    holidays = []

    # New Year's Day - January 1
    nyd = date(year, 1, 1)
    holidays.append(_adjust_for_weekend_observed(nyd))

    # Martin Luther King Jr. Day - Third Monday in January
    holidays.append(_nth_weekday(year, 1, 0, 3))  # 0=Monday, 3rd occurrence

    # Presidents' Day - Third Monday in February
    holidays.append(_nth_weekday(year, 2, 0, 3))

    # Memorial Day - Last Monday in May
    holidays.append(_last_weekday(year, 5, 0))

    # Juneteenth - June 19
    juneteenth = date(year, 6, 19)
    holidays.append(_adjust_for_weekend_observed(juneteenth))

    # Independence Day - July 4
    july4 = date(year, 7, 4)
    holidays.append(_adjust_for_weekend_observed(july4))

    # Labor Day - First Monday in September
    holidays.append(_nth_weekday(year, 9, 0, 1))

    # Columbus Day - Second Monday in October
    holidays.append(_nth_weekday(year, 10, 0, 2))

    # Veterans Day - November 11
    veterans = date(year, 11, 11)
    holidays.append(_adjust_for_weekend_observed(veterans))

    # Thanksgiving - Fourth Thursday in November
    holidays.append(_nth_weekday(year, 11, 3, 4))  # 3=Thursday, 4th occurrence

    # Christmas Day - December 25
    christmas = date(year, 12, 25)
    holidays.append(_adjust_for_weekend_observed(christmas))

    return holidays


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """Find the nth occurrence of a weekday in a month."""
    first_day = date(year, month, 1)
    first_weekday = first_day.weekday()

    # Days until first occurrence of target weekday
    days_until = (weekday - first_weekday) % 7
    first_occurrence = first_day + timedelta(days=days_until)

    # Add weeks to get nth occurrence
    return first_occurrence + timedelta(weeks=n - 1)


def _last_weekday(year: int, month: int, weekday: int) -> date:
    """Find the last occurrence of a weekday in a month."""
    last_day = date(year, month, monthrange(year, month)[1])
    days_back = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=days_back)


def _adjust_for_weekend_observed(d: date) -> date:
    """
    If holiday falls on Saturday, observed on Friday.
    If holiday falls on Sunday, observed on Monday.
    """
    if d.weekday() == 5:  # Saturday
        return d - timedelta(days=1)
    elif d.weekday() == 6:  # Sunday
        return d + timedelta(days=1)
    return d


class DeadlineCalculator:
    """
    Calculates USPTO response deadlines with extension fees.

    USPTO Rules:
    - Standard response period: 6 months from mailing date (absolute max)
    - Shortened Statutory Period (SSP): Usually 3 months for non-final actions
    - Extensions available in 1-month increments up to 6 months total
    - If deadline falls on weekend/holiday, moves to next business day
    - Final Office Actions may have different/limited extension options
    """

    # USPTO Extension Fees (2024/2025) in USD
    # These should be updated annually when USPTO publishes new fee schedules
    EXTENSION_FEES = {
        1: {"micro": 220, "small": 440, "large": 880},
        2: {"micro": 640, "small": 1280, "large": 2560},
        3: {"micro": 1480, "small": 2960, "large": 5920},
        4: {"micro": 2320, "small": 4640, "large": 9280},
        5: {"micro": 3160, "small": 6320, "large": 12640},
    }

    def __init__(self):
        self._holiday_cache = {}

    def _get_holidays_for_year(self, year: int) -> List[date]:
        """Get holidays for a year with caching."""
        if year not in self._holiday_cache:
            self._holiday_cache[year] = get_us_federal_holidays(year)
        return self._holiday_cache[year]

    def _is_holiday(self, d: date) -> bool:
        """Check if a date is a US federal holiday."""
        holidays = self._get_holidays_for_year(d.year)
        return d in holidays

    def _add_months(self, d: date, months: int) -> date:
        """
        Add months to a date, handling month-end edge cases.
        If the resulting day doesn't exist in the target month,
        use the last day of that month.
        """
        target_month = d.month + months
        target_year = d.year + (target_month - 1) // 12
        target_month = ((target_month - 1) % 12) + 1

        # Handle day overflow (e.g., Jan 31 + 1 month = Feb 28/29)
        max_day = monthrange(target_year, target_month)[1]
        target_day = min(d.day, max_day)

        return date(target_year, target_month, target_day)

    def _adjust_for_weekend_holiday(self, d: date) -> date:
        """Move date to next business day if on weekend or holiday."""
        while d.weekday() >= 5 or self._is_holiday(d):
            d += timedelta(days=1)
        return d

    def calculate_deadlines(
        self,
        mailing_date: date,
        shortened_period_months: int = 3,
        is_final_action: bool = False
    ) -> DeadlineCalculation:
        """
        Calculate all deadline tiers from the mailing date.

        Args:
            mailing_date: The Office Action mailing date
            shortened_period_months: The shortened statutory period (default 3 months)
            is_final_action: Whether this is a Final Office Action

        Returns:
            DeadlineCalculation with all deadline tiers
        """
        tiers = []
        notes = []
        today = date.today()

        logger.info(f"Calculating deadlines for mailing date: {mailing_date}, SSP: {shortened_period_months} months")

        # Calculate tiers from SSP to 6 months
        for month_offset in range(shortened_period_months, 7):
            raw_deadline = self._add_months(mailing_date, month_offset)
            adjusted_deadline = self._adjust_for_weekend_holiday(raw_deadline)

            # Check if adjustment was needed
            if raw_deadline != adjusted_deadline:
                notes.append(
                    f"{month_offset}-month deadline adjusted from {raw_deadline.isoformat()} "
                    f"to {adjusted_deadline.isoformat()} (weekend/holiday)"
                )

            extension_months = month_offset - shortened_period_months

            if extension_months == 0:
                fees = {"micro": 0, "small": 0, "large": 0}
            else:
                fees = self.EXTENSION_FEES.get(
                    extension_months,
                    self.EXTENSION_FEES[5]  # Cap at 5-month extension fees
                )

            tier = DeadlineTier(
                deadline_date=adjusted_deadline.isoformat(),
                months_from_mailing=month_offset,
                months_extension=extension_months,
                extension_fee_micro=fees["micro"],
                extension_fee_small=fees["small"],
                extension_fee_large=fees["large"],
                is_past=adjusted_deadline < today
            )
            tiers.append(tier)

        # Add notes for final actions
        if is_final_action:
            notes.append(
                "This is a Final Office Action. Consider filing an RCE or Appeal "
                "if extensions beyond the statutory period are needed."
            )

        statutory_deadline = tiers[0].deadline_date if tiers else mailing_date.isoformat()
        maximum_deadline = tiers[-1].deadline_date if tiers else mailing_date.isoformat()

        return DeadlineCalculation(
            mailing_date=mailing_date.isoformat(),
            shortened_statutory_period=shortened_period_months,
            statutory_deadline=statutory_deadline,
            maximum_deadline=maximum_deadline,
            tiers=tiers,
            notes=notes,
            is_final_action=is_final_action
        )

    def calculate_from_string(
        self,
        mailing_date_str: str,
        shortened_period_months: int = 3,
        is_final_action: bool = False
    ) -> DeadlineCalculation:
        """
        Calculate deadlines from a date string.

        Args:
            mailing_date_str: Date string in various formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
            shortened_period_months: The shortened statutory period (default 3 months)
            is_final_action: Whether this is a Final Office Action

        Returns:
            DeadlineCalculation with all deadline tiers
        """
        # Parse the date string
        mailing_date = self._parse_date(mailing_date_str)
        return self.calculate_deadlines(mailing_date, shortened_period_months, is_final_action)

    def _parse_date(self, date_str: str) -> date:
        """Parse a date string in various formats."""
        import re

        # Clean the string
        date_str = date_str.strip()

        # Try ISO format first (YYYY-MM-DD)
        iso_match = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", date_str)
        if iso_match:
            year, month, day = map(int, iso_match.groups())
            return date(year, month, day)

        # Try US format (MM/DD/YYYY or M/D/YYYY)
        us_match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", date_str)
        if us_match:
            month, day, year = map(int, us_match.groups())
            return date(year, month, day)

        # Try common USPTO format (Month DD, YYYY)
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        text_match = re.match(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", date_str)
        if text_match:
            month_str, day, year = text_match.groups()
            month = month_names.get(month_str.lower())
            if month:
                return date(int(year), month, int(day))

        raise ValueError(f"Unable to parse date: {date_str}")


# Singleton instance
deadline_calculator = DeadlineCalculator()
