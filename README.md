Written in Python 3.6.1 using a Redis database.

## Setup

Download the folder go to it in the terminal
```
$ cd /path/to/project
```

Ensure redis is installed. For MacOS:
```
$ brew install redis
```

For linux:
```
$ apt-get install redis-server
```

Create Python 3.6.1 virtualenv:
```
$ virtualenv -p path/to/python/binary env
```

Install requirements
```
$ pip install -r requirements.txt
```

Run tests
```
$ fab test
```

Run the development server for testing.
```
$ fab dev_server
```

When you're done stop the redis server
```
$ fab stop_server
```

## Scaling

The code would run on a gunicorn web server behind an nginx reverse proxy. We may need multiple servers handling requests in a cluster behind a load balancer.


The project could be put in a docker image The database would run on a redis cluster. This can handle higher throughput and provides redundancy if a server goes down. It would also increases the available RAM for the database.

With more time, I would containerise the application. This lets us quickly implement the same environment on new machines. This could be orchestrated with kubernetes.



## How it works

####Terminology
- link - A pointer to a website which has a long_url, short_url and id
- long_url - The original url we need to store (String)
- id - Unique identifier of the link in our database (Integer)
- short_url - The encoded form of the id used in the shortened url. (String A-Z a-z 0-9)



The server uses a redis database. Three different types of data are stored in the database:
#### long_urls_by_id
Each key is a unique integer ID and the value is the corresponding long url. When a request is made to our server with a short url, we decode the short url to get the id and use this id to find the long url.


#### ids_by_long_url
Each key is a long url and the value is the corresponding id. When a request is made to create a new short url, we need
to check if a short url already exists and if so what its id is. When a new short url is created an entry is added to
both long_urls_by_id and ids_by_long_url together they work as a two way dictionary

### id_counter
We need to store each url at a unique id. We could use a single counter but this could become a bottleneck when there 
is a large amount of traffic. Instead we have hundreds of separate counters each allocating a different range of ids. The counter used by an individual request is picked randomly. This setup means the data can easily be partitioned across machines.

Although redis backs up to disk and is persistent the entire data is stored in memory. Despite each url using only a
small amount of memory, over time memory usage may become an issue.

## Example API usage:
```

curl -d '{"url": "http://helloworld.com"}'
     -X POST http://localhost:5000/shorten_url
     -H "Content-Type: application/json"



Request:
    POST http://localhost:8000/shorten_url

    body:
    {
        "url": "www.helloworld.com"
    }

Response: 
    Status code: 201
    response_body:
    {
        "shortened_url": 'http://localhost:8000/ouoYFY48'
    }
```


`http://localhost:8000/ouoYFY48` -> 302 Redirect to www.helloworld.com


