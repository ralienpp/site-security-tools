site-security-tools
===================

A set of tools to enhance the security of web-sites.


Rationale
=========

Software such as Samhain or Tripwire already solves this problem, 
however these programs are not always applicable. For example, when 
you're using a shared hosting service, you are most likely running
inside a sandboxed environment, you cannot install third-party 
software, etc.

`site-security-tools` are self-contained instruments that don't 
require anything except a standard Python 2.x installation (tested
with 2.7 installed from sources).



dirwatcher
----------

Watch the file system for changes such as the creation of new files,
removal or editing of existing ones.

The tool is meant to be ran at regular intervals, via something like
`cron`. When differences are detected, Cron will send an email 
with dirwatcher's output. It will tell you which files were affected,
so you can have a look.

If there were no changes, there will be no notifications.


The check is done by building a tree and MD5 hashing each file. Trees
produced in subsequent runs will be compared with the previous
data and differences will be reported by email (provided that 
your cron is configured to do that).


TODO
----

- add option to watch multiple directories, or get the directory
  to watch via a command line argument, then create multiple
  cron jobs for each dir you're interested in.

- add file filtering by masks

- check file sizes before hashing, only hash if the size changed
