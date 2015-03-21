Svnlog is a python script to get more info from the subversion log.
It allows advanced filtering (by author, by message) and more verbose outputs (diffs).

## Usage Examples ##
Show normal svn log:
```
$ svnlog
```

Show diffs for every commit (very verbose):
```
$ svnlog -vv
```

Filter by message:
```
$ svnlog -m '^Fixed'
```

Filter by authors:
```
$ svnlog -a ken,dennis
```

Filter by an exact day:
```
$ svnlog -D -7
```
