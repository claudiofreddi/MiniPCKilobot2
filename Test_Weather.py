# import the module


import python_weather
import python_weather.enums

import asyncio
import os
from Socket_Utils_Text import Translate

async def getweather():
  # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
  async with python_weather.Client(unit=python_weather.METRIC,locale=python_weather.enums.Locale.ITALIAN) as client:
    # fetch a weather forecast from a city
    weather = await client.get('Milan')
    
    # returns the current day's forecast temperature (int)
    print(weather.temperature)
    print(Translate(str(weather.kind)))
    
    # get the weather forecast for a few days
    for daily in weather.daily_forecasts:
      print(daily)
      
      # hourly forecasts
      for hourly in daily.hourly_forecasts:
        print(f' --> {hourly!r}')

if __name__ == '__main__':
  # see https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
  # for more details
  if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
  
  asyncio.run(getweather())