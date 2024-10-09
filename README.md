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

## Caveats

Obviously this is a very rough-and-ready little snippet. It blindly calls `eval` on whatever is in that events array file, so malicious (or really any) code in there can ruin your day, hide your keys, steal your car, or break up with your loved ones. 


## Maintenance

None is intended. Feel free to open issues or PRs, but please don't expect timely (or any) review. 

