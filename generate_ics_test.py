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
            },
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

if __name__ == "__main__":
    unittest.main()