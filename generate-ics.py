import argparse
import json
import os
from icalendar import Calendar, Event
from icalendar.prop import vRecur
from datetime import datetime, timedelta
import pytz

# Function to create the .ics file
def create_ics(events, output_file):
    cal = Calendar()

    for event in events:
        if "dates" in event:  # If the event has multiple specific dates
            for date_str in event["dates"]:
                ical_event = Event()
                ical_event.add("summary", event["summary"])

                event_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                ical_event.add("dtstart", event_date)
                ical_event.add("dtend", event_date + timedelta(days=1))  # All-day event ends next day

                cal.add_component(ical_event)

        elif "date_start" in event and "date_end" in event:
            # Multi-day event
            start_date = datetime.strptime(event["date_start"], "%d.%m.%Y").date()
            end_date = datetime.strptime(event["date_end"], "%d.%m.%Y").date()

            ical_event = Event()
            ical_event.add("summary", event["summary"])
            ical_event.add("dtstart", start_date)
            ical_event.add("dtend", end_date + timedelta(days=1))  # End date is exclusive

            cal.add_component(ical_event)

        elif "recurrence" in event:
            # Handle recurring events
            ical_event = Event()
            ical_event.add("summary", event["summary"])
            
            start_date = datetime.strptime(event["date"], "%d.%m.%Y").date()
            ical_event.add("dtstart", start_date)
            ical_event.add("dtend", start_date + timedelta(days=1))  # All-day event ends next day
            
            # Add recurrence rule
            rrule = vRecur(freq=event["recurrence"]["freq"], interval=event["recurrence"]["interval"])
            if "count" in event["recurrence"]:
                rrule['COUNT'] = event["recurrence"]["count"]  # Number of occurrences
            if "until" in event["recurrence"]:
                until_date = datetime.strptime(event["recurrence"]["until"], "%d.%m.%Y").date()
                rrule['UNTIL'] = until_date

            ical_event.add("rrule", rrule)

            cal.add_component(ical_event)

        else:
            # Single-day event
            event_date = datetime.strptime(event["date"], "%d.%m.%Y").date()

            ical_event = Event()
            ical_event.add("summary", event["summary"])
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

    # Load the events array from the input file
    if os.path.exists(args.input_file):
        with open(args.input_file, "r") as f:
            events = {}
            exec(f.read(), {}, events)  # Execute the input file safely in a controlled environment
            events = events["events"]  # Get the "events" variable from the executed code
            if isinstance(events, dict) and "events" in events:
                events = events["events"]  # Safely get the array if defined in a dictionary
    else:
        print(f"Error: File {args.input_file} not found.")
        return

    # Call the function to create the .ics file
    create_ics(events, args.output_file)
    print(f".ics file created: {args.output_file}")

if __name__ == "__main__":
    main()

