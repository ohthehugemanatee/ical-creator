events = [
    # Single-day event
    {"summary": "Trödelmarkt", "date": "18.10.2024", "start_time": "10:00", "end_time": "12:00" },
    # One event that occurs on multiple days that don't match a simple rule
    {"summary": "Weihnachtssingen", "dates": ["25.11.2024", "02.12.2024", "09.12.2024", "16.12.2024"]},
    # Multi-day event
    {"summary": "Weihnachtsschließzeit", "date_start": "23.12.2024", "date_end": "31.12.2024"},
    # Recurring event every 2 weeks
    {"summary": "Biweekly Event", "date": "01.02.2025", "recurrence": {"freq": "WEEKLY", "interval": 2,  "until": "01.06.2025"}}
]

exceptions = [
            {"title": "Mom's birthday", "date_start": "02.01.2023", "date_end": "02.01.2023"},
            {"date_start": "05.01.2023", "date_end": "05.01.2023", "reason": "Public holiday"}
        ]
