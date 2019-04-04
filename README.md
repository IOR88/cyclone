# Docker


# Deployment
provide settings for database
```python
DATABASE_HOST = 'localhost'
DATABASE_PORT = '5432'
DATABASE_NAME = 'cyclone'
DATABASE_USER = 'admin'
DATABASE_PASSWORD = '1234'

```
create database schema (run model.py as main file)
```bash
$(virtualenv) python ../models.py
```

run scrapy (will save extracted data to postgresql database)
```bash
$(virtualenv) scrapy crawl cyclone_spider
```

# Modelling(thoughts)
* For cyclone entity we have just provided a name flag, which is extracted from http://rammb.cira.colostate.edu, we are not totally sure about name **re(\w{2})(\d{2})(\d{4})**, it seems that first group corresponds to geographical area, the last to year, the middle one could be the day of a year or maybe unique cyclone identifier. **We mention this because we haven't implemented cyclone movement element, we are not sure if scenario like this is contained in tracking data.** 

* From http://rammb.cira.colostate.edu we know that 3 forecast centers bring information for cyclones, and from there we know that some forecast centers share the same oceans area but still tracking data is not associated with any forecast center, at least not on the rammb page. **Forecast entity has a relationship to forecast center but it is NULL true for a moment**.
