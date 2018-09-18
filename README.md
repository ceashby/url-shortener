## Setup

Download the folder, open the terminal and cd into that directory
```
cd /path/to/project
```

Ensure redis is installed. For MacOS:
```
brew install redis
```

For linux:
```
apt-get install redis-server
```

Create Python 3.6.1 virtualenv:
```
virtualenv -p path/to/python/binary env
```

Enter virtual environment:
```
source env/bin/activate 
```

Install requirements
```
pip install -r requirements.txt
```

Run tests
```
fab test
```

Run the development server for testing.
```
fab dev_server
```

When you're done stop the redis server
```
fab stop_server
```

## How it works

####Terminology
- link - A pointer to a website which has a long_url, short_url and id
- long_url - The original url we need to store (String)
- id - The unique identifier of the link in our database (Integer)
- short_url - The encoded form of the id used in the shortened url. (String A-Z a-z 0-9)

### Database

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

## Example API usage:
```
curl -d '{"url": "http://example.com"}'
     -X POST http://localhost:5000/shorten_url
     -H "Content-Type: application/json"

Request:
    POST http://localhost:5000/shorten_url

    body:
    {
        "url": "http://example.com"
    }

Response: 
    Status code: 201
    response_body:
    {
        "shortened_url": 'http://localhost:5000/abcde'
    }
```


`http://localhost:8000/abcde` -> 302 Redirect to http://example.com



## Scaling

There are two types of process which need to run.

- HTTP Server
The flask dev server is not designed for production. In production the code would run on gunicorn servers that manages the creation of request handling processes. We may need multiple servers handling requests in a cluster. To implement this we would put them behind a load balancer. Requests to our service would hit the load balancer and be forwarded to a specific node.  I would containerise the application and deploy it in a kubernetes cluster with an ingress.

- Redis DB
Redis normally runs on one machine but to scale (both storage and throughput) we would create a cluster of redis instances using Redis Cluster. These would run inside the kubernetes cluster. Using a redis cluster also provides redundancy so the entire database remains available even when a node goes down.

Although redis backs up to disk and is persistent all data is stored in memory. Despite each url using a tiny amount of memory, over time memory usage would become an issue. An on disk solution would be required such as Cassandra or Aerospike. Of the two I would use Aerospike as it is particularly suited to large numbers of reads and writes with small amounts of data. Regardless of database used to store the keys and values the same design principles apply.