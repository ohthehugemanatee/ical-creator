import argparse
import os
from icalendar import Calendar, Event
from icalendar.prop import vRecur
from datetime import datetime, timedelta

# Function to create the .ics file
def create_ics(events, output_file, exceptions=[]):
    cal = Calendar()
    # Convert exceptions to a set of dates for easy lookup
    exception_dates = set()
    for exception in exceptions:
        start_date = datetime.strptime(exception["date_start"], "%d.%m.%Y").date()
        end_date = datetime.strptime(exception["date_end"], "%d.%m.%Y").date()
        current_date = start_date
        while current_date <= end_date:
            exception_dates.add(current_date)
            current_date += timedelta(days=1)

    for event in events:
        if "dates" in event:  # If the event has multiple specific dates
            for date_str in event["dates"]:
                event_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                if event_date in exception_dates:
                    continue
                ical_event = Event()
                ical_event.add("summary", event["summary"], parameters={"CHARSET": "UTF-8"})
                if "description" in event:
                    ical_event.add("description", event["description"], parameters={"CHARSET": "UTF-8"})
                if "start_time" in event and "end_time" in event:
                    start_datetime = datetime.strptime(date_str + " " + event["start_time"], "%d.%m.%Y %H:%M")
                    end_datetime = datetime.strptime(date_str + " " + event["end_time"], "%d.%m.%Y %H:%M")
                    ical_event.add("dtstart", start_datetime)
                    ical_event.add("dtend", end_datetime)
                else:
                    ical_event.add("dtstart", event_date)
                    ical_event.add("dtend", event_date + timedelta(days=1))  # All-day event ends next day

                cal.add_component(ical_event)

        elif "date_start" in event and "date_end" in event:
            # Multi-day event
            start_date = datetime.strptime(event["date_start"], "%d.%m.%Y").date()
            end_date = datetime.strptime(event["date_end"], "%d.%m.%Y").date()

            ical_event = Event()
            ical_event.add("summary", event["summary"], parameters={"CHARSET": "UTF-8"})
            if "description" in event:
                ical_event.add("description", event["description"], parameters={"CHARSET": "UTF-8"})
            if "start_time" in event and "end_time" in event:
                start_datetime = datetime.combine(start_date, datetime.strptime(event["start_time"], "%H:%M").time())
                end_datetime = datetime.combine(end_date, datetime.strptime(event["end_time"], "%H:%M").time())
                ical_event.add("dtstart", start_datetime)
                ical_event.add("dtend", end_datetime)
                exdates = [datetime.combine(date, start_datetime.time()) for date in exception_dates if start_date <= date <= end_date]
            else:
                ical_event.add("dtstart", start_date)
                ical_event.add("dtend", end_date + timedelta(days=1))  # End date is exclusive
                exdates = [date for date in exception_dates if start_date <= date <= end_date]

            if exdates:
                ical_event.add("exdate", exdates)

            cal.add_component(ical_event)

        elif "recurrence" in event:
            # Handle recurring events
            ical_event = Event()
            ical_event.add("summary", event["summary"], parameters={"CHARSET": "UTF-8"})
            if "description" in event:
                ical_event.add("description", event["description"], parameters={"CHARSET": "UTF-8"})
            event_date = datetime.strptime(event["date"], "%d.%m.%Y").date()
            if "start_time" in event and "end_time" in event:
                start_datetime = datetime.combine(event_date, datetime.strptime(event["start_time"], "%H:%M").time())
                end_datetime = datetime.combine(event_date, datetime.strptime(event["end_time"], "%H:%M").time())
                ical_event.add("dtstart", start_datetime)
                ical_event.add("dtend", end_datetime)
                exdates = [datetime.combine(date, start_datetime.time()) for date in exception_dates if date >= event_date]
            else:
                ical_event.add("dtstart", event_date)
                ical_event.add("dtend", event_date + timedelta(days=1))  # All-day event ends next day
                exdates = [date for date in exception_dates if date >= event_date]

            # Add recurrence rule
            rrule = vRecur(freq=event["recurrence"]["freq"], interval=event["recurrence"]["interval"])
            if "count" in event["recurrence"]:
                rrule['COUNT'] = event["recurrence"]["count"]  # Number of occurrences
            if "until" in event["recurrence"]:
                until_date = datetime.strptime(event["recurrence"]["until"], "%d.%m.%Y").date()
                rrule['UNTIL'] = until_date

            ical_event.add("rrule", rrule)
            if exdates:
                ical_event.add("exdate", exdates)

            cal.add_component(ical_event)

        else:
            # Single-day event
            event_date = datetime.strptime(event["date"], "%d.%m.%Y").date()
            if event_date not in exception_dates:
                ical_event = Event()
                ical_event.add("summary", event["summary"], parameters={"CHARSET": "UTF-8"})
                if "description" in event:
                    ical_event.add("description", event["description"], parameters={"CHARSET": "UTF-8"})
                if "start_time" in event and "end_time" in event:
                    start_datetime = datetime.combine(event_date, datetime.strptime(event["start_time"], "%H:%M").time())
                    end_datetime = datetime.combine(event_date, datetime.strptime(event["end_time"], "%H:%M").time())
                    ical_event.add("dtstart", start_datetime)
                    ical_event.add("dtend", end_datetime)
                else:
                    ical_event.add("dtstart", event_date)
                    ical_event.add("dtend", event_date + timedelta(days=1))  # All-day event ends next day

                cal.add_component(ical_event)

    with open(output_file, 'wb') as f:
        f.write(cal.to_ical())


# Main function to handle arguments and file processing
def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Generate an .ics file from an events array.")
    parser.add_argument("input_file", help="Path to the Python file containing the events array.")
    parser.add_argument("output_file", help="Desired output .ics file name.")

    args = parser.parse_args()
    file_content_parsed = {}
    events = []
    exceptions = []
    # Load the arrays from the input file
    if os.path.exists(args.input_file):
        with open(args.input_file, "r") as f:
            file_content = f.read()
            # Parsed contents of the events file. This could be a naked array or a dict with keys for "events" and optionally, exceptions
            exec(file_content, {}, file_content_parsed)
            # Extract from keys if it's a dict
            if "events" in file_content_parsed:
                events = file_content_parsed["events"]
                # Exceptions array is optional
                if "exceptions" in file_content_parsed:
                    exceptions = file_content_parsed["exceptions"]
            # Otherwise, assume it's a naked array
            else:
                events = eval(file_content)
                # Exceptions cannot be defined in this case.

    else:
        print(f"Error: File {args.input_file} not found.")
        return

    # Call the function to create the .ics file
    create_ics(events, args.output_file, exceptions)
    print(f".ics file created: {args.output_file}")

if __name__ == "__main__":
    main()

