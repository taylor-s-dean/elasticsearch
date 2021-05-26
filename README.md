```
$ isearch.py --help
usage: isearch.py [-h] [--index str] [--number-of-results int] [--es-url str] [--query str] str

positional arguments:
  str                   ISO country code to filter on

optional arguments:
  -h, --help            show this help message and exit
  --index str           Name of ElasticSearch index to use
  --number-of-results int
                        Number of search results to display
  --es-url str          URL and port of ElasticSearch
  --query str           Provide a custom search query with placeholders for QUERY_TEXT, SIZE, and COUNTRY
```

```
isearch.py GB --index 'location-v0-en' --number-of-results 5 --es-url 'http://localhost:9200'
```

```
> Glasgow
Glasgow, Glasgow City, Scotland, United Kingdom             (population:   591620, parent_population:   615070, type:    LOCATION_TYPE_PPL, id:  23085779, score: 206.062)
Port Glasgow, Inverclyde, Scotland, United Kingdom          (population:    15190, parent_population:    79160, type:    LOCATION_TYPE_PPL, id:  23000173, score: 126.527)
Provanmill, Glasgow, Glasgow City, Scotland, United Kingdom (population:        0, parent_population:   591620, type:   LOCATION_TYPE_PPLX, id:  34584517, score: 48.9439)
Polmadie, Glasgow, Glasgow City, Scotland, United Kingdom   (population:        0, parent_population:   591620, type:   LOCATION_TYPE_PPLX, id:  34584518, score: 48.9439)
Tradeston, Glasgow, Glasgow City, Scotland, United Kingdom  (population:        0, parent_population:   591620, type:   LOCATION_TYPE_PPLX, id:  34584514, score: 48.5547)
```

```
isearch.py GB --index 'location-v0-en' --number-of-results 5 --es-url 'http://localhost:9200' --query '{"size": SIZE, "query": {"match": {"name": "QUERY_TEXT"}}}'
```

```
> Glasgow
Glasgow, Grange Hill, Westmoreland, Jamaica                                                 (population:        0, parent_population:     9703, type:    LOCATION_TYPE_PPL, id:  22424445, score: 14.0291)
Glasgow, Ontario, Canada                                                                    (population:        0, parent_population: 12861940, type:    LOCATION_TYPE_PPL, id:  22203591, score: 14.0291)
Glasgow, White Hall, Saint Thomas, Jamaica                                                  (population:        0, parent_population:     1878, type:    LOCATION_TYPE_PPL, id:  22424104, score: 14.0282)
Glasgow, Essequibo Islands-West Demerara Region, Guyana                                     (population:        0, parent_population:   107416, type:    LOCATION_TYPE_PPL, id:  21842599, score: 14.0282)
Glasgow, Weverly, Nuwara Eliya Division, Nuwara Eliya District, Central Province, Sri Lanka (population:        0, parent_population:        0, type:    LOCATION_TYPE_PPL, id:  24958598, score: 14.0282)
```
