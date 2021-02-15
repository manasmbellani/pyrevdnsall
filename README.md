# pyrevdnsall
Python script to perform reverse dns on /24 or other ranges obtained from subdomains/IPs to locate more subdomains

## Setup

## Via Docker

build the docker image first
```
docker build -t pyrevdnsall:latest .
```

## Usage 

### Via Docker

To expand the IPs/ranges/domains in file: `/opt/dockershare/pyrevdnsall/inputs.txt` recursively in reverse, run the command:
```
docker run -v /opt/dockershare:/opt/dockershare -t --rm pyrevdnsall:latest -i /opt/dockershare/pyrevdnsall/inputs.txt
```