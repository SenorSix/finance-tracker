The objective of this script is to take the messy description column out of CSV files from the bank and clean them up so they're concise and readable. 

Originally I tried having the script automate it but it was pretty messy still and skipped a lot of vendors. I tried different things with varying success but it was lackluster results. 

After looking over the CSV file, I started to notice patterns in the descriptions so I went through and created a mental idea of how a script could approach all the descriptions and get a high rate of automated results. Eliminating total manual intervention is impossible unless you're okay with with some messy outputs. I took those messy outputs and put them into a JSON file for the script to reference and replace those outputs with a cleaner output. There were still some oddball descriptions that the script didn't handle and I refined further to account for those until I could run the script with 100% automation. Without further testing with new data, it appears that the script will handle future edge case well and I will modify in the future accordingly.

Details about the script:

The CSV file has a majority of descriptions with POS PURCHASE with the vendor immediately following. The script first goes through the column of descriptions identifying descriptions with POS PURCHASE in them and copies, up to two words, the vendor to the new column. If it runs into a non alphabetical character it stops copying. 

If the first character after POS PURCHASE is not an alphabetical character, the script puts XXXX into the new column for further manual review. For instance if the vendor is 5GUYS, XXXX is copied into the new column. Further down the script individual cases like this are examined and automated.

After the POS PURCHASE problem was solved there were some edge cases to handle. 5GUYS results in XXXX and of course the several transactions that don't have POS PURCHASE within the descriptions. I noticed that most of the non POS PURCHASE transactions had the business right at the start so that was the next natural instance to automate. the output wasn't perfect but it was pretty good. 

So now I had a new column with a majority of the outputs automated with a good handful of edge cases and some sloppy outputs. The solution to this is a JSON file that I put sloppy outputs in and change it to a more desirable output. The script then runs through the new column, finds the sloppy outputs like Mcm Leasing and changes it to something clearer like Paycheck.

All the above handled a majority of transactions but I still had edge cases like my XXXX output for further review, a new Xx output that resulted from XX being at the beginning of several descriptions, and an sq output that I hadn't noticed yet. Now the script takes these instances and checks them against another JSON file created for these special cases and gives desirable outputs. 

After this I achieved 100% automation with the data I had



This project uses two JSON files to clean and correct vendor names from bank transaction descriptions:

clean_names.json
Used for standard cleanups of vendor names.

Matches against the output of the extract_vendor() function.

Keys are in Title Case (e.g., "Mcm Leasing"), matching the formatting of the cleaned vendor names.

Example:

{
  "Mcm Leasing": "Paycheck",
  "Xfinity Mobile": "Xfinity"
}

fallback_map.json
Handles edge cases where the vendor name couldn't be extracted properly (e.g., XXXX, Xx, Sq).

Matches against the full original description, converted to lowercase.

Keys are lowercase substrings to catch broader patterns.

Example:

{
  "credit cash app": "Cash App +",
  "5guys": "Five Guys"
}
These two files work together to clean vendor names with high accuracy and flexibility.