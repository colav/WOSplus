# WOS+

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/e9e840f8451e4894884c70a6759ff3a6)](https://www.codacy.com/app/restrepo/WOSplus?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=restrepo/WOSplus&amp;utm_campaign=Badge_Grade) 

Load data bases from [Web of Science](https://www.webofknowledge.com), [Scopus](https://www.scopus.com), [Scielo](https://www.webofknowledge.com), etc, and combine the results into a single data base

For WOSplus execution it is recommended to define `drive.cfg` file in which you can specify the name of the files and its shared keys in Google drive. The `drive.cfg` file must be present in the execution folder. For example
``` bash
$ cat drive.cfg
[FILES]
CIB_Scielo.xlsx    = 0BxoOXsn2EUNIMldPUFlwNkdLOTQ
```
See also the `drive.cfg` file in the test folder which gives some addresses of sample databases stored in google drive. If the file is not found in the google drive cloud, it is searched and loaded locally, by using just the name of the file.
## Installation
Python 3 is required
``` bash
# pip install wosplus
```

## Visual Overview
![design](./internal/inherit-diagram.svg)
