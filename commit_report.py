#!/usr/bin/env python
########################################################################################################################
#
# This is a tool that takes a repository URL and two commit hashes, identifies all the commits in between them, and
# outputs that list of commits along with the commit message, author, and timestamp for each. The tool supports
# both human-readable and machine-readable output formats.
#
# Author: Tim Laurence
# Date: Mat 3rd, 2017
#
########################################################################################################################
import argparse
import base64
import os
import json
import traceback
from collections import namedtuple
from sys import argv
import re
import sys
from git import Repo, Commit

# Holds processed commit information
CommitData = namedtuple('CommitData', 'id, author, timestamp, messages, issues')
# Holds processed issue information
IssueData = namedtuple('IssueData', 'id display')

DEFAULT_ISSUE_ID_MATCHER = '(?P<display>\[(?P<id>[^]]+)\])'
DEFAULT_LINK_TEMPLATE = '{display} : https://jira.com/browse/{id}'
DEFAULT_CACHE_DIR = ".cache/"


def clone_repo(url: str, cache_path: str) -> Repo:
    """
    Clone a remote repo to a local path
    :param url: The remote repo URI
    :param cache_path: A local filesystem path to clone to
    :return: A Repo object
    """
    return Repo.clone_from(url=url, to_path=cache_path)


def refresh_repo(path: str) -> Repo:
    """
    Perform a fetch on a repo already locally cached
    :param path: The patch shere the repo is locallt cached
    :return: The now 'fetched' repo object
    """
    repo = Repo(path=path)
    repo.remote().update()
    return repo


def is_local_repo(uri: str) -> bool:
    return not re.match('^(https?://|git@|git://)', uri, re.IGNORECASE)


def create_cache_path(uri: str) -> str:
    return '{cache_dir}{uri}'.format(cache_dir=DEFAULT_CACHE_DIR,
                                     uri=base64.urlsafe_b64encode(uri.encode('ascii')).decode('ascii'))


def get_repo(uri: str) -> Repo:
    """
    This take a path to a repo, local or remote and returns a pythongit Repo object
    If the path is remote it fetches and refreshes as needed.
    :param uri: Path to local or remote repo 
    :return: Repo object
    """

    if is_local_repo(uri):
        return Repo(uri)

    cache_path = create_cache_path(uri=uri)
    if os.path.isdir(cache_path):
        repo = refresh_repo(cache_path)
    else:
        repo = clone_repo(url=uri, cache_path=cache_path)
    return repo


def process_commit(commit: Commit, include_links: bool, issue_id_matcher: str = DEFAULT_ISSUE_ID_MATCHER) -> CommitData:
    """
    Convert and format commit object into Commitdata object for easier use
    :param commit: The commit being worked on
    :param include_links: Should we look for jira issues to link to later 
    :param issue_id_matcher: Regex to identify Jira issues. Should return 'id' and 'display' groups 
    :return: CommitData object
    """
    if include_links:
        issues = [IssueData(id=found.group('id').lower(), display=found.group('display')) for found in
                  re.finditer(re.compile(issue_id_matcher), commit.message)]
    else:
        issues = []

    return CommitData(id=commit.binsha.hex(),
                      author=commit.author.name,
                      timestamp=commit.authored_datetime.strftime("%x %X"),
                      messages=commit.message,
                      issues=issues)


def generate_link_list(template: str, issues: [IssueData]) -> [str]:
    """
    Applies link template to a list of Issues
    :param template: 
    :param issues: 
    :return: List of rendered strings
    """
    return [template.format(**issue._asdict()) for issue in issues]


def format_for_humans(commitdata: CommitData,
                      include_links: bool = False,
                      link_template: str = DEFAULT_LINK_TEMPLATE) -> str:
    """
    Format output in human pleasing way
    :param commitdata: List of Commitdata objects
    :param include_links: Boolean indictaed weather we want to display Jira links
    :param link_template: String which template to format Jira links
    :return: Multiline string suitable for output
    """

    lines = []
    for commit in commitdata:
        message_padding = '\n' + (80 * ' ')
        lines.append("{id} {author:20.20} {timestamp} {messages}".format(
            id=commit.id,
            author=commit.author,
            timestamp=commit.timestamp,
            messages=commit.messages.rstrip().replace('\n', message_padding)  # Line up multiple messages
        ))
        if include_links and commit.issues:
            lines.append('Linked Jira Issues:')
            lines.extend(generate_link_list(template=link_template, issues=commit.issues))
        lines.append('')
    return '\n'.join(lines)


def format_for_json(commitdata: CommitData,
                    include_links: bool = False,
                    link_template: str = DEFAULT_LINK_TEMPLATE) -> str:
    """
    Format output is json
    :param commitdata: List of Commitdata objects
    :param include_links: Boolean indictaed weather we want to display Jira links
    :param link_template: String which template to format Jira links
    :return: json string in format
    """

    objs = []
    for commit in commitdata:
        obj = {"id": commit.id,
               "author": commit.author,
               "timestamp": commit.timestamp,
               "messages": commit.messages}
        if include_links and commit.issues:
            obj['issue_links'] = generate_link_list(template=link_template, issues=commit.issues)
        objs.append(obj)
    return json.dumps(objs)


def parse_args(args: [str]) -> argparse.Namespace:
    """
    Parse command line arguments
    :param args: Commandline arguments
    :return: Namespace object containing parsed arguments
    """
    parser = argparse.ArgumentParser(description='Simple reports on the commit ranges')

    validate_group = parser.add_mutually_exclusive_group(required=False)
    validate_group.add_argument('--human',
                                dest='formatter',
                                action='store_const',
                                const=format_for_humans,
                                help='Human readable output (default)'
                                )

    validate_group.add_argument('--json',
                                dest='formatter',
                                action='store_const',
                                const=format_for_json,
                                help='Json formatted output'
                                )

    parser.set_defaults(formatter=format_for_humans)

    parser.add_argument('--issue-links',
                        dest='links',
                        action='store_true',
                        default=False,
                        help='Display links to issue tracker')

    parser.add_argument('--issue-matcher',
                        dest='issue_id_regex',
                        action='store',
                        default=DEFAULT_ISSUE_ID_MATCHER,
                        help='Regex describing issue identifiers (Default: "%(default)s")')

    parser.add_argument('--link-template',
                        dest='link_template',
                        action='store',
                        default=DEFAULT_LINK_TEMPLATE,
                        help='Format strong for issue links (Default: "%(default)s")')

    parser.add_argument('repo', metavar='REPO_URI/PATH', help='Git repo to analyze')
    parser.add_argument(dest='start', metavar='START_COMMIT', help='commit range start')
    parser.add_argument(dest='end', metavar='END_COMMIT', help='commit range end')

    if len(args) < 3:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args(args=args)


def do_it(args: [str]):
    """
    This does most of the work parsing args and generating reports. This is seperated from main to improve testability 
    :param args: Arguments passed in
    :return: None
    """
    try:
        parsed_args = parse_args(args)
        repo = get_repo(parsed_args.repo)
        commit_iter = repo.iter_commits(rev='{start}...{end}'.format(start=parsed_args.start, end=parsed_args.end))
        processed_commits = [process_commit(commit, parsed_args.links, issue_id_matcher=parsed_args.issue_id_regex) for
                             commit in commit_iter]
        print(parsed_args.formatter(processed_commits, parsed_args.links, parsed_args.link_template))
    except Exception as e:
        print('Sorry, we ran into the following error: {}'.format(e))
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    do_it(argv[1:])
