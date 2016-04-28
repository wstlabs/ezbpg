Test Data
---------

'simple.csv' is a small sample data set that exercises some basic connectivity cases. 

'null.csv' is an empty data set.

The 'nychpd-' and 'dhcr-' datasets are real-world uses cases that initially inspired this tool.  Each file represents extracts of two columns for two different property identifiers (BBL and BIN) as used by various NYC property databases.  In principle these are usually 1-1, and sometimes 1-to-many (that is, sometimes there are multiple BINs per BBL); but due to data quality issues (incorrect BBLs and BINs coming from various sources) there were small clusters of many-to-many combinations of these keys which were causing us significant headaches. 

So in order to satisfy ourselves that we understood what was really going (and being as we had no a priori information as to how these keys should related to one another), we wrote this little tool.

Lastly: NYCHPD and DHCR are two separate NYC agencies (look them up).  As to the identifiers:  BBL is a tax lot identifier, and BIN is (one of) the building identification numbers used throughout the NYC municipal data ecosystem.  And the "-clean" and "-dirty" modifiers on the dataset signify the fact that one of each is relatively unfilitered (with respect to e.g. blank lines or null columns); however, both will parse (though the output for one will be significiantly noisier than that of the other). 



