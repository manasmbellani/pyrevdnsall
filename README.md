# pyrevdnsall
Python script to perform reverse dns on /24 or other ranges obtained from subdomains/IPs to locate more subdomains

## Setup

## Via Docker

```
docker build -t pyrevdnsall:latest .
```

## Usage 

### Via Docker

```
docker run -v /opt/dockershare:/opt/dockershare -t --rm pyrevdnsall:latest -i /opt/dockershare/pyrevdnsall/inputs.txt
```