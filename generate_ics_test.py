import unittest
import os
from generate_ics import create_ics
from icalendar import Calendar


class TestHelloWorld(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual("hello", "hello")

class TestGenerateICS(unittest.TestCase):

    def setUp(self):
        self.output_file = "test_output.ics"
        self.events = [
            {
                "summary": "Single Day Event",
                "date": "01.01.2023"
            },
            {
                "summary": "Multi Day Event",
                "date_start": "01.01.2023",
                "date_end": "03.01.2023"
            },
            {
                "summary": "Recurring Event",
                "date": "01.01.2023",
                "recurrence": {
                    "freq": "DAILY",
                    "interval": 1,
                    "count": 5
                }
            },
            {
                "summary": "Multiple Specific Dates Event",
                "dates": ["01.01.2023", "05.01.2023", "10.01.2023"]
            }
        ]
        self.exceptions = [
            {"date_start": "02.01.2023", "date_end": "02.01.2023"},
            {"date_start": "05.01.2023", "date_end": "05.01.2023"}
        ]

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_create_ics_file(self):
        create_ics(self.events, self.output_file)
        self.assertTrue(os.path.exists(self.output_file))

    def test_single_day_event(self):
        create_ics([self.events[0]], self.output_file)
        with open(self.output_file, 'rb') as f:
            ical_content = f.read().decode()
        self.assertIn("SUMMARY:Single Day Event", ical_content)
        self.assertIn("DTSTART;VALUE=DATE:20230101", ical_content)
        self.assertIn("DTEND;VALUE=DATE:20230102", ical_content)

    def test_multi_day_event(self):
        create_ics([self.events[1]], self.output_file)
        with open(self.output_file, 'rb') as f:
            ical_content = f.read().decode()
        self.assertIn("SUMMARY:Multi Day Event", ical_content)
        self.assertIn("DTSTART;VALUE=DATE:20230101", ical_content)
        self.assertIn("DTEND;VALUE=DATE:20230104", ical_content)

    def test_recurring_event(self):
        create_ics([self.events[2]], self.output_file)
        with open(self.output_file, 'rb') as f:
            ical_content = f.read()
        
        ical_content_text = ical_content.decode()
        self.assertIn("SUMMARY:Recurring Event", ical_content_text)
        self.assertIn("DTSTART;VALUE=DATE:20230101", ical_content_text)
        self.assertIn("DTEND;VALUE=DATE:20230102", ical_content_text)
        # Actually load the RRULE to validate it
        ical_content_cal = Calendar.from_ical(ical_content)
        found_rrule = False

        for component in ical_content_cal.walk():
            if component.name == "VEVENT":
                if "RRULE" in component:
                    rrule = component["RRULE"]
                    self.assertEqual(rrule["FREQ"][0], "DAILY")
                    self.assertEqual(rrule["INTERVAL"][0], 1)
                    self.assertEqual(rrule["COUNT"][0], 5)
                    found_rrule = True

        self.assertTrue(found_rrule)

    def test_multiple_specific_dates_event(self):
        create_ics([self.events[3]], self.output_file)
        with open(self.output_file, 'rb') as f:
            ical_content = f.read().decode()
        self.assertIn("SUMMARY:Multiple Specific Dates Event", ical_content)
        self.assertIn("DTSTART;VALUE=DATE:20230101", ical_content)
        self.assertIn("DTSTART;VALUE=DATE:20230105", ical_content)
        self.assertIn("DTSTART;VALUE=DATE:20230110", ical_content)

    def test_exceptions(self):   
        create_ics(self.events, self.output_file, self.exceptions)
        with open(self.output_file, 'rb') as f:
            ical_content = f.read().decode()

        cal = Calendar.from_ical(ical_content)

        single_day_event_dates = []
        multi_day_event_dates = []
        recurring_event_exdates = []
        multiple_specific_dates_event_dates = []

        for component in cal.walk():
            if component.name == "VEVENT":
                summary = component.get("SUMMARY")
                dtstart = component.get("DTSTART").dt.strftime("%Y%m%d")
                if summary == "Single Day Event":
                    single_day_event_dates.append(dtstart)
                elif summary == "Multi Day Event":
                    multi_day_event = component
                elif summary == "Recurring Event":
                    if "EXDATE" in component:
                        exdate = component.get("EXDATE")
                        exdate_values = exdate.dts
                        recurring_event_exdates = [dt.dt.strftime("%Y%m%d") for dt in exdate_values]
                elif summary == "Multiple Specific Dates Event":
                    multiple_specific_dates_event_dates.append(dtstart)

        self.assertIn("20230101", single_day_event_dates)
        self.assertEqual(multi_day_event.get("DTSTART").dt.strftime("%Y%m%d"), "20230101")
        self.assertEqual(multi_day_event.get("DTEND").dt.strftime("%Y%m%d"), "20230104")  # End date is exclusive
        exdate = multi_day_event.get("EXDATE")
        self.assertIsNotNone(exdate)
        exdate_values = exdate.dts
        multi_day_event_exdates = [dt.dt.strftime("%Y%m%d") for dt in exdate_values]
        self.assertIn("20230102", multi_day_event_exdates)
        self.assertIn("20230102", recurring_event_exdates)
        self.assertIn("20230105", recurring_event_exdates)
        self.assertIn("20230101", multiple_specific_dates_event_dates)
        self.assertIn("20230110", multiple_specific_dates_event_dates)
        self.assertNotIn("20230105", multiple_specific_dates_event_dates)

    def test_single_day_event_with_time(self):
        event_with_time = {
            "summary": "Single Day Event with Time",
            "date": "01.01.2023",
            "start_time": "10:00",
            "end_time": "12:00"
        }
        create_ics([event_with_time], self.output_file)
        with open(self.output_file, 'rb') as f:
            ical_content = f.read().decode()

        cal = Calendar.from_ical(ical_content)
        for component in cal.walk():
            if component.name == "VEVENT":
                self.assertEqual(component.get("SUMMARY"), "Single Day Event with Time")
                self.assertEqual(component.get("DTSTART").dt.strftime("%Y%m%dT%H%M%S"), "20230101T100000")
                self.assertEqual(component.get("DTEND").dt.strftime("%Y%m%dT%H%M%S"), "20230101T120000")

    def test_multi_day_event_with_time(self):
        event_with_time = {
            "summary": "Multi Day Event with Time",
            "date_start": "01.01.2023",
            "date_end": "03.01.2023",
            "start_time": "09:00",
            "end_time": "17:00"
        }
        create_ics([event_with_time], self.output_file)
        with open(self.output_file, 'rb') as f:
            ical_content = f.read().decode()

        cal = Calendar.from_ical(ical_content)
        for component in cal.walk():
            if component.name == "VEVENT":
                self.assertEqual(component.get("SUMMARY"), "Multi Day Event with Time")
                self.assertEqual(component.get("DTSTART").dt.strftime("%Y%m%dT%H%M%S"), "20230101T090000")
                self.assertEqual(component.get("DTEND").dt.strftime("%Y%m%dT%H%M%S"), "20230103T170000")

    def test_recurring_event_with_time(self):
        event_with_time = {
            "summary": "Recurring Event with Time",
            "date": "01.01.2023",
            "start_time": "08:00",
            "end_time": "09:00",
            "recurrence": {
                "freq": "DAILY",
                "interval": 1,
                "count": 5
            }
        }
        create_ics([event_with_time], self.output_file)
        with open(self.output_file, 'rb') as f:
            ical_content = f.read().decode()

        cal = Calendar.from_ical(ical_content)
        for component in cal.walk():
            if component.name == "VEVENT":
                self.assertEqual(component.get("SUMMARY"), "Recurring Event with Time")
                self.assertEqual(component.get("DTSTART").dt.strftime("%Y%m%dT%H%M%S"), "20230101T080000")
                self.assertEqual(component.get("DTEND").dt.strftime("%Y%m%dT%H%M%S"), "20230101T090000")
                self.assertEqual(component.get("RRULE")["FREQ"][0], "DAILY")
                self.assertEqual(component.get("RRULE")["INTERVAL"][0], 1)
                self.assertEqual(component.get("RRULE")["COUNT"][0], 5)

    def test_multiple_specific_dates_event_with_time(self):
        event_with_time = {
            "summary": "Multiple Specific Dates Event with Time",
            "dates": ["01.01.2023", "05.01.2023", "10.01.2023"],
            "start_time": "14:00",
            "end_time": "16:00"
        }
        create_ics([event_with_time], self.output_file)
        with open(self.output_file, 'rb') as f:
            ical_content = f.read().decode()

        cal = Calendar.from_ical(ical_content)
        for component in cal.walk():
            if component.name == "VEVENT":
                self.assertEqual(component.get("SUMMARY"), "Multiple Specific Dates Event with Time")
                dtstart = component.get("DTSTART").dt.strftime("%Y%m%dT%H%M%S")
                dtend = component.get("DTEND").dt.strftime("%Y%m%dT%H%M%S")
                self.assertIn(dtstart, ["20230101T140000", "20230105T140000", "20230110T140000"])
                self.assertIn(dtend, ["20230101T160000", "20230105T160000", "20230110T160000"])


if __name__ == "__main__":
    unittest.main()