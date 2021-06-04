# geo-spider

crawl all GEO metadata, features:

1. crawl platforms
2. crawl samples
3. crawl series
4. incremental crawling
5. missed crawling

Table of Contents

1. [installation](#installation)
2. [output file format](#output-file-format)
3. [logs](#logs)
4. [platforms](#platforms)
   - [denovo crawling](#platforms-denovo-crawling)
   - [incremental crawling](#platforms-incremental-crawling)
   - [missed crawling](#platforms-missed-crawling)
5. [samples](#samples)
   - [denovo crawling](#samples-denovo-crawling)
   - [incremental crawling](#samples-incremental-crawling)
   - [missed crawling](#samples-missed-crawling)
6. [series](#series)
   - [denovo crawling](#series-denovo-crawling)
   - [incremental crawling](#series-incremental-crawling)
   - [missed crawling](#series-missed-crawling)

## installation

```
pip install geo-spider
```

## output file format

geo-spider saves files in jsonlines form,
Refer to [this site](https://jsonlines.org/) for details.

## logs

geo-spider default generate logs to geo-spider.log(current directory)
in WARNING level, you can customize by `-d` and `-l` options.

1. `-d` to enable debug mode
2. `-l` specify customized log file

```
geo-spider -d -l new-geo-spider.log <sub-command>
```

## platforms

### platforms denovo crawling

```
geo-spider platforms -o platforms.jl
```

### platforms incremental crawling

If you have a crawled platforms jsonlines file:

```
geo-spider platforms -cf platforms.jl -o new-platforms.jl
```

If you have multiple platforms jsonlines files:

```
geo-spider platforms -cd platforms -o new-platforms.jl
```

### platforms missed crawling

Specify `-cf` or `-cd` like incremental crawling, add a `-m` option.

```
geo-spider platforms -cf platforms.jl -m missed -o new-platforms.jl
```

## samples

### samples denovo crawling

### samples incremental crawling

### samples missed crawling

## series

### series denovo crawling

### series incremental crawling

### series missed crawling
