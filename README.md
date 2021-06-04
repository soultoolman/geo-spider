# geo-spider

crawl all GEO metadata, features:

1. crawl platforms
2. crawl samples
3. crawl series
4. incremental crawling

1. [installation](#installation)
2. [output file format](#output-file-format)
3. [platforms](#platforms)
   - [denovo crawling](#platforms-denovo-crawling)
   - [incremental crawling](#platforms-incremental-crawling)
4. [samples](#samples)
   - [denovo crawling](#samples-denovo-crawling)
   - [incremental crawling](#samples-incremental-crawling)
5. [series](#series)
   - [denovo crawling](#series-denovo-crawling)
   - [incremental crawling](#series-incremental-crawling)

## installation

```
pip install geo-spider
```

## output file format

geo-spider saves files in jsonlines form,
Refer to [this site](https://jsonlines.org/) for details.

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

## samples

### samples denovo crawling

### samples incremental crawling

### series

### series denovo crawling

### series incremental crawling
