"""
Actuator: Real iCalendar (.ics RFC 5545) Schedule Generator.
Converts Mirror Future mathematical prescriptions into optimal, synchronizable,
and downloadable time blocks for Google Calendar, Apple Calendar, and Microsoft Outlook.
"""

import uuid
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Union
import pytz
from icalendar import Calendar, Event, Alarm, vText
from app.models.schemas import OptimalTimeBlock, CalendarIcsResponse, InverseEngineeringPrescription


class CalendarWriter:
    """
    Production-grade .ics schedule generator.
    Creates calendar events with explicit timezones, proactive fatigue-prevention alarms,
    and cognitive focus block categorizations.
    """

    def __init__(self, timezone_str: str = "America/Bogota"):
        try:
            self.tz = pytz.timezone(timezone_str)
        except Exception:
            self.tz = pytz.UTC

    def create_calendar(self, calendar_name: str = "Mirror Future - Optimal Causal Schedule") -> Calendar:
        """Initializes a VCALENDAR object conforming to RFC 5545."""
        cal = Calendar()
        cal.add("prodid", "-//Mirror Future//Causal Life Engine 2.0//EN")
        cal.add("version", "2.0")
        cal.add("calscale", "GREGORIAN")
        cal.add("method", "PUBLISH")
        cal.add("x-wr-calname", vText(calendar_name))
        cal.add("x-wr-timezone", vText(self.tz.zone))
        cal.add("x-wr-caldesc", vText("Protected time blocks for thesis, career, and rest optimized by Mirror Future."))
        return cal

    def add_block_event(self, cal: Calendar, block: OptimalTimeBlock) -> Event:
        """
        Appends a structured time block event with alarms and strict iCalendar properties.
        """
        event = Event()
        event.add("summary", block.title)
        event.add("description", block.description)

        # Ensure timezone-aware datetimes
        start_dt = block.start_time
        if start_dt.tzinfo is None:
            start_dt = self.tz.localize(start_dt)

        end_dt = block.end_time
        if end_dt.tzinfo is None:
            end_dt = self.tz.localize(end_dt)

        event.add("dtstart", start_dt)
        event.add("dtend", end_dt)
        event.add("dtstamp", datetime.now(self.tz))
        event.add("uid", f"mirror-future-{uuid.uuid4()}@{self.tz.zone}")
        event.add("status", "CONFIRMED")
        event.add("categories", [block.category, "MIRROR_FUTURE_CAUSAL"])
        if block.location:
            event.add("location", block.location)

        # OPAQUE marks the slot as busy in calendar clients
        event.add("transp", "OPAQUE")

        # Proactive cognitive preparation alarm
        if block.alarm_minutes_before > 0:
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add("description", f"Mirror Future Alert: Starting {block.title}")
            alarm.add("trigger", -timedelta(minutes=block.alarm_minutes_before))
            event.add_component(alarm)

        cal.add_component(event)
        return event

    def generate_optimal_blocks_from_prescription(
        self,
        prescription: InverseEngineeringPrescription,
        start_date: Optional[date] = None,
        num_days: int = 14,
    ) -> List[OptimalTimeBlock]:
        """
        Translates mathematically prescribed hours into realistic, circadian-aligned weekly blocks:
        1. Protected Morning Research / Thesis Block (peak mental acuity).
        2. Strict-Capped Corporate Work Shift (hard daily boundary).
        3. Relational Buffer & Personal Life Decompression.
        4. Protected Sleep & Digital Disconnect Block.
        """
        base_date = start_date or date.today()
        blocks: List[OptimalTimeBlock] = []

        thesis_duration = timedelta(hours=prescription.optimal_daily_thesis_hours)
        work_duration = timedelta(hours=prescription.optimal_daily_work_cap_hours)

        for day_offset in range(num_days):
            current_day = base_date + timedelta(days=day_offset)
            is_weekend = current_day.weekday() in (5, 6)

            if not is_weekend:
                # 1. Protected Thesis / Deep Work Block (from 07:30 AM)
                thesis_start = datetime.combine(current_day, time(7, 30))
                thesis_end = thesis_start + thesis_duration
                blocks.append(
                    OptimalTimeBlock(
                        title="🎯 Mirror Future | Protected Research & Deep Work Block (Zero Notifications)",
                        description=(
                            "Priority cognitive block determined by the causal engine. "
                            f"Target: {prescription.optimal_daily_thesis_hours}h deep progress before external demands."
                        ),
                        category="THESIS",
                        start_time=thesis_start,
                        end_time=thesis_end,
                        alarm_minutes_before=15,
                        location="Quiet Study / Deep Work Space"
                    )
                )

                # 2. Corporate Work Block with Strict Upper Cap
                work_start = datetime.combine(current_day, time(10, 0))
                work_end = work_start + work_duration
                blocks.append(
                    OptimalTimeBlock(
                        title=f"💼 Mirror Future | Corporate Work Shift (Strict Cap {prescription.optimal_daily_work_cap_hours:.1f}h)",
                        description=(
                            f"Strict mathematical cap prescribed to prevent P90 Burnout. "
                            f"Non-negotiable cutoff: {work_end.strftime('%H:%M')}."
                        ),
                        category="DEEP_WORK",
                        start_time=work_start,
                        end_time=work_end,
                        alarm_minutes_before=10,
                        location="Office / Remote"
                    )
                )

                # 3. Relational Buffer / Social Recharge
                relational_start = work_end + timedelta(minutes=45)
                relational_end = relational_start + timedelta(hours=2, minutes=0)
                blocks.append(
                    OptimalTimeBlock(
                        title="❤️ Mirror Future | Relational Buffer & Personal Life",
                        description="Active maintenance of social capital. Connecting with key bonds, shared dinner, or rest.",
                        category="RELATIONAL_BUFFER",
                        start_time=relational_start,
                        end_time=relational_end,
                        alarm_minutes_before=0,
                        location="Home / Social Setting"
                    )
                )

            else:
                # Weekend: Decoupling and restorative recovery
                recovery_start = datetime.combine(current_day, time(10, 0))
                recovery_end = recovery_start + timedelta(hours=3, minutes=0)
                blocks.append(
                    OptimalTimeBlock(
                        title="🌿 Mirror Future | Regenerative Recharge & Guilt-Free Leisure",
                        description="Nervous system protection. Alleviation of accumulated autoregressive cognitive fatigue.",
                        category="REST",
                        start_time=recovery_start,
                        end_time=recovery_end,
                        alarm_minutes_before=0
                    )
                )

        return blocks

    def export_to_ics_string(self, blocks: List[OptimalTimeBlock], calendar_name: str = "Mirror Future - Optimal Causal Schedule") -> str:
        """Generates plain text RFC 5545 calendar stream."""
        cal = self.create_calendar(calendar_name)
        for block in blocks:
            self.add_block_event(cal, block)
        return cal.to_ical().decode("utf-8")

    def export_to_response(
        self,
        blocks: List[OptimalTimeBlock],
        filename: str = "optimal_schedule_mirror_future.ics"
    ) -> CalendarIcsResponse:
        """Builds a complete Pydantic contract ready for HTTP download."""
        raw_ics = self.export_to_ics_string(blocks)
        return CalendarIcsResponse(
            ics_raw=raw_ics,
            filename=filename,
            total_blocks=len(blocks)
        )

    def write_to_file(self, blocks: List[OptimalTimeBlock], file_path: str) -> str:
        """Physically writes the .ics calendar file to local storage."""
        raw_ics = self.export_to_ics_string(blocks)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(raw_ics)
        return file_path


# Default singleton instance
calendar_actuator = CalendarWriter()
