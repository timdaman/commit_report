# Git Reporting tool
This tools generates reports about the commits between two commit hashes. In other word it shows all the commits applied to the first commit that are needed to create the second commit

# Installation

1. Install the python requirements using pip, 
   `pip install -r requirements.txt`
2. Add execute permissions to commit_report.py if needed 
   `chmod u+x commit_report.py`

# How to use
    usage: commit_report.py [-h] [--human | --json] [--issue-links]
                            [--issue-matcher ISSUE_ID_REGEX]
                            [--link-template LINK_TEMPLATE]
                            REPO_URI/PATH START_COMMIT END_COMMIT
    
    Simple reports on the commit ranges
    
    positional arguments:
      REPO_URI/PATH         Git repo to analyze
      START_COMMIT          commit range start
      END_COMMIT            commit range end
    
    optional arguments:
      -h, --help            show this help message and exit
      --human               Human readable output (default)
      --json                Json formatted output
      --issue-links         Display links to issue tracker
      --issue-matcher ISSUE_ID_REGEX
                            Regex describing issue identifiers (Default: "(?P<display>\[(?P<id>[^]]+)\])")
      --link-template LINK_TEMPLATE
                            Format strong for issue links (Default: "{display} : https://jira.com/browse/{id}")

## Examples

For these examples the commit log looks like so
      
      99bae718d623d8e2b7a64296b54e70c39699745b -> #Inital commit
      b5e0316329d8f546707990deb91ee77353f1ccd4 ->
      6bf1ec411f5bb159c0cc9e02215ec0d3856344cd ->
      794ac3fc424c98fb5ac422ab1ea89b83e065d65c ->
      06b0bb0d68514272fbe6a4c081b00fae364ccbb5    # Latest commit

### Simple report showing the difference between two commits
    $ python3 commit_report.py git@example.com:test.git 99bae718d623d8e2b7a64296b54e70c39699745b 6bf1ec411f5bb159c0cc9e02215ec0d3856344cd
    6bf1ec411f5bb159c0cc9e02215ec0d3856344cd Tim Laurence         05/02/17 01:45:07 Test [SWTI-23] 4
    
    b5e0316329d8f546707990deb91ee77353f1ccd4 Tim Laurence         05/02/17 01:44:17 Test 3 [SWTI-23]

### Simple report with multi-line and blank messages
    $ python3 commit_report.py  git@localhost:test.git 6bf1ec411f5bb159c0cc9e02215ec0d3856344cd 06b0bb0d68514272fbe6a4c081b00fae364ccbb5
    06b0bb0d68514272fbe6a4c081b00fae364ccbb5 Tim Laurence         05/02/17 01:48:52 Test 6.1
                                                                                    Test 6.2
    
    794ac3fc424c98fb5ac422ab1ea89b83e065d65c Tim Laurence         05/02/17 01:47:29 

### Same report adding issue tracker link list
    $ python3 commit_report.py --issue-links git@localhost:test.git 99bae718d623d8e2b7a64296b54e70c39699745b 6bf1ec411f5bb159c0cc9e02215ec0d3856344cd
    6bf1ec411f5bb159c0cc9e02215ec0d3856344cd Tim Laurence         05/02/17 01:45:07 Test [SWTI-23] 4
    Linked Jira Issues:
    [SWTI-23] : https://jira.com/browse/swti-23
    
    b5e0316329d8f546707990deb91ee77353f1ccd4 Tim Laurence         05/02/17 01:44:17 Test 3 [SWTI-23]
    Linked Jira Issues:
    [SWTI-23] : https://jira.com/browse/swti-23

### Same report adding issue custom tracker link list
    $ python3 commit_report.py --link-template 'https://example.com/issue{id}' --issue-links git@localhost:test.git 99bae718d623d8e2b7a64296b54e70c39699745b 6bf1ec411f5bb159c0cc9e02215ec0d3856344cd
    6bf1ec411f5bb159c0cc9e02215ec0d3856344cd Tim Laurence         05/02/17 01:45:07 Test [SWTI-23] 4
    Linked Jira Issues:
    https://example.com/issueswti-23
    
    b5e0316329d8f546707990deb91ee77353f1ccd4 Tim Laurence         05/02/17 01:44:17 Test 3 [SWTI-23]
    Linked Jira Issues:
    https://example.com/issueswti-23

### Same report adding with custom matcher
    $ python3 commit_report.py --issue-matcher '(?P<display>Test (?P<id>\d+))' --issue-links git@localhost:test.git 99bae718d623d8e2b7a64296b54e70c39699745b 6bf1ec411f5bb159c0cc9e02215ec0d3856344cd
    6bf1ec411f5bb159c0cc9e02215ec0d3856344cd Tim Laurence         05/02/17 01:45:07 Test [SWTI-23] 4
    
    b5e0316329d8f546707990deb91ee77353f1ccd4 Tim Laurence         05/02/17 01:44:17 Test 3 [SWTI-23]
    Linked Jira Issues:
    Test 3 : https://jira.com/browse/3
    
### Output formatted in json
    $ python3 commit_report.py --json --issue-matcher '(?P<display>Test (?P<id>\d+))' --issue-links git@localhost:test.git 99bae718d623d8e2b7a64296b54e70c39699745b 6bf1ec411f5bb159c0cc9e02215ec0d3856344cd
    [{"id": "6bf1ec411f5bb159c0cc9e02215ec0d3856344cd", "author": "Tim Laurence", "timestamp": "05/02/17 01:45:07", "messages": "Test [SWTI-23] 4\n"}, {"id": "b5e0316329d8f546707990deb91ee77353f1ccd4", "author": "Tim Laurence", "timestamp": "05/02/17 01:44:17", "messages": "Test 3 [SWTI-23]\n", "issue_links": ["Test 3 : https://jira.com/browse/3"]}]

# How to run tests
To allow more complete testing all tests are run inside a docker container that is being presented a simulated git server.

## Requirements
* docker
* docker-compose

## Running the test

1. `docker-compose build`
2. `docker-compose up -d`
3. wait about 10 seconds
4. `docker-compose logs app` to see the test results
5. clean-up containers with `docker-compose down`

