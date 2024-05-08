import requests
from bs4 import BeautifulSoup
import datetime

def fetch_gate_closing_times():
    url = 'https://www.dnv.org/parks-trails-recreation/hiking-and-cycling-trails-parks'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('h3', string='Parking at Fromme Mountain').find_next('table')
    closing_times = {}
    for row in table.find_all('tr')[1:]:  # Skip header row
        cols = row.find_all('td')
        date_range = cols[0].text.strip()
        time = cols[1].text.strip()
        closing_times[date_range] = time

    return closing_times

def get_current_closing_time(closing_times):
    now = datetime.datetime.now()
    for date_range, time in closing_times.items():
        start_date, end_date = date_range.split(' to ')
        start_date = datetime.datetime.strptime(f"{start_date} {now.year}", '%B %d %Y')
        end_date = datetime.datetime.strptime(f"{end_date} {now.year}", '%B %d %Y')

        # Adjust for year wrap-around
        if end_date < start_date:
            if now < start_date:
                end_date = datetime.datetime.strptime(f"{end_date.strftime('%B %d')} {now.year - 1}", '%B %d %Y')
            else:
                end_date = datetime.datetime.strptime(f"{end_date.strftime('%B %d')} {now.year + 1}", '%B %d %Y')

        if start_date <= now <= end_date:
            # Convert time to 24-hour format
            closing_time_24hr = datetime.datetime.strptime(time, '%I%p').strftime('%H:%M')
            return closing_time_24hr
    return 'Closing time not found'

def calculate_time_until_closing(closing_time):
    now = datetime.datetime.now()
    closing_time_today = datetime.datetime.strptime(closing_time, '%H:%M')
    closing_datetime = datetime.datetime(now.year, now.month, now.day,
                                         closing_time_today.hour, closing_time_today.minute)
    if now > closing_datetime:
        closing_datetime += datetime.timedelta(days=1)  # Move to the next day if past closing
    remaining_time = closing_datetime - now
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes = remainder // 60
    return f"{hours} hours and {minutes} minutes until closing"

def main():
    closing_times = fetch_gate_closing_times()
    current_closing_time = get_current_closing_time(closing_times)
    if current_closing_time != 'Closing time not found':
        countdown = calculate_time_until_closing(current_closing_time)
        print(countdown)
    else:
        print(current_closing_time)

if __name__ == '__main__':
    main()