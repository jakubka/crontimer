#!/usr/bin/env python3

import sys
import re


class TimeOfDay:
    """
    Represents time of the day with no date specified and with precision up to minutes. This class is immutable.
    """

    def __init__(self, hour, minute):
        assert(0 <= hour <= 23)
        assert(0 <= minute <= 59)

        self.hour = hour
        self.minute = minute

    def is_earlier_than(self, other_time_of_day):
        return self.get_minute_of_day() < other_time_of_day.get_minute_of_day()

    def get_minute_of_day(self):
        return self.hour * 60 + self.minute

    def __str__(self):
        return "{0:d}:{1:02d}".format(self.hour, self.minute)

    @staticmethod
    def parse(text):
        match = re.match(r"^(?P<hour>[01]?[0-9]|2[0-3]):(?P<minute>[0-5][0-9])$", text)
        if match:
            return TimeOfDay(int(match.group("hour")), int(match.group("minute")))
        else:
            return None

def generate_cron_times(hour, minute):
    minutes = range(0, 60) if minute == '*' else [int(minute)]
    hours = range(0, 24) if hour == '*' else [int(hour)]

    return (TimeOfDay(h, m) for h in hours for m in minutes)


def find_next_run_time(current_time, cron_times):
    # times in the same day will go first
    sorted_times = sorted(cron_times,
                          key=lambda time: 1 if time.is_earlier_than(current_time) else 0)

    return sorted_times[0]


def get_output(current_time, command, cron_hour, cron_minute):
    cron_times = generate_cron_times(cron_hour, cron_minute)

    next_run_time = find_next_run_time(current_time, cron_times)

    day = "tomorrow" if next_run_time.is_earlier_than(current_time) else "today"

    return "{0} {1} - {2}".format(next_run_time, day, command)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Parameter specifying current time required in format HH:MM")
        sys.exit(2)

    current_time = TimeOfDay.parse(sys.argv[1])

    if not current_time:
        print("Cannot parse current time")
        sys.exit(2)

    input_regex = re.compile(r"^(?P<cron_minute>[0-5]?[0-9]|\*) (?P<cron_hour>[012]?[0-9]|\*) (?P<cron_command>.*)$")

    for input_line in sys.stdin:
        match = input_regex.match(input_line)
        if match:
            cron_minute = match.group("cron_minute")
            cron_hour = match.group("cron_hour")
            command = match.group("cron_command")

            output = get_output(current_time, command, cron_hour, cron_minute)
            print(output)
        else:
            print("Invalid input")
