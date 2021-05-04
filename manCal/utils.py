# calendarapp/utils.py

from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Event
from myProject.helper import get_current_user
import datetime
from django.utils.timezone import make_aware

""" creation of calendar that extend HTML calendar """
class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None, user=None):
		self.year = year
		self.month = month
		self.user = user
		super(Calendar, self).__init__()

	# formats a day as a td
	# filter events by day
	""" creating days and inserting event in the day  """
	def formatday(self, day, events, year , month, user):
		events_per_day = events.filter(start_time__day=day)
		eventsAll = Event.objects.filter(user=user)
		d = ''
		
		
		if day != 0:
			""" recunstructing full date time of the creting day to then filter events """
			dt_start = datetime.datetime(year, month, day)
			tm_start = datetime.time(23, 59)
			combined_start = dt_start.combine(dt_start, tm_start)
			dt_end = datetime.datetime(year, month, day)
			tm_end = datetime.time(00, 1)
			combined_end = dt_end.combine(dt_end, tm_end)
			
			for event in eventsAll:
				""" check which events are still ongoing on the day """
				if event.start_time <= combined_start and event.end_time >= combined_end:
					d += f'<li> {event.get_html_url} </li>'	
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr 
	""" creating week rows """
	def formatweek(self, theweek, events, year, month, user):
		week = ''
		for d, weekday in theweek:
			week += self.formatday(d, events, year, month, user)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	""" first function that created the calendar """
	def formatmonth(self, withyear=True,):

		user = self.user
		""" events filtered to show only those that are created by the logged user """
		events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month).filter(user=user)
		

		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events, self.year, self.month, user )}\n'
		return cal