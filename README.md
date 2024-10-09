# ICAL Creator

I frequently get stupidly-formatted lists of key dates and holidays from my kids' activities and school. ChatGPT is great at reading photos of arbitrary formats and converting them to python arrays. This is a little scriptie to convert that python array into an .ics file for easy import into your calendar of choice. 

It's basically just a CLI wrapper around the python [icalendar library](https://pypi.org/project/icalendar/).

## Usage

`python3 generate_ics.py events_array.py output.ics`

The script requires two positional arguments:

- a valid python file containing (just) an array of calendar events to create
- the desired filename for your output .ics 

### Events array format

The events array can be just a variable, or a variable explicitly named `events`, at your preference. It should contain objects for each event that will end up in the ICS, formatted appropriately for the [icalendar library](https://pypi.org/project/icalendar/). I've included an example file in this repo.


### Prompt to create the array

Here's a prompt you can use to create the array from your arbitrary image or PDF or whatever. Modify to suit the format you're providing, because every input is different. One school gives a stupid calendar-ish layout, another club gives a table, another activity gives a bullet list, and they all give me a headache.


    The attached file contains a table of events, with each row specifying a date or range of dates, an event name, and additional details such as a summary or notes. I would like to extract these events into a Python array that follows this structure:
    
    ```python
    events = [
        {
            "summary": "Event Name",
            "date": "dd.mm.yyyy",  # For single-day events
        },
        {
            "summary": "Multi-day Event Name",
            "date_start": "dd.mm.yyyy",
            "date_end": "dd.mm.yyyy",  # For multi-day events
        },
        {
            "summary": "Repeating Event Name",
            "dates": ["dd.mm.yyyy", "dd.mm.yyyy", ...]  # For events that occur on multiple, non-consecutive dates
        }
    ]
    ```
    
    ### Additional information:
    - For single-day events, use `"date"`.
    - For multi-day events, use `"date_start"` and `"date_end"`.
    - For events that occur on multiple specific dates, use a `"dates"` list.
    - The event name should be used for the `"summary"`, and if there are any notes or remarks, they should be included in parentheses as part of the summary (e.g., `summary: "Event Name (Notes)"`).
    
    Can you help me extract this information from the file I'll provide? The dates are in the European format (dd.mm.yyyy). Please return the Python array of events.


## Caveats

Obviously this is a very rough-and-ready little snippet. It blindly calls `eval` on whatever is in that events array file, so malicious (or really any) code in there can ruin your day, hide your keys, steal your car, or break up with your loved ones. 


## Maintenance

None is intended. Feel free to open issues or PRs, but please don't expect timely (or any) review. 

