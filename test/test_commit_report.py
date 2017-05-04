import argparse
import json
import os
import sys
import textwrap
import unittest
from unittest.mock import patch
import shutil
from git import Repo

__author__ = 'tim'

import commit_report


class TestRepo(unittest.TestCase):
    def setUp(self):
        self.local_repo = 'test/test.git'
        self.remote_repo = 'git@git-server:test.git'
        self.cache_path = '.cache/Z2l0QGdpdC1zZXJ2ZXI6dGVzdC5naXQ='
        self.commit_start = '9c83a8a26c3bcd517d310b1a2a4d0a48a1af2ada'
        self.commit_end = '06b0bb0d68514272fbe6a4c081b00fae364ccbb5'

    def test_is_local_repo(self):
        self.assertEqual(commit_report.is_local_repo('/blaa'), True)
        self.assertEqual(commit_report.is_local_repo('blaa/'), True)
        self.assertEqual(commit_report.is_local_repo('/blgitaa'), True)
        self.assertEqual(commit_report.is_local_repo('gitblass'), True)
        self.assertEqual(commit_report.is_local_repo('git@github.com:UserName/Example.git'), False)
        self.assertEqual(commit_report.is_local_repo('https://UserName@github.com/UserName/Example.git'), False)
        self.assertEqual(commit_report.is_local_repo('http://UserName@github.com/UserName/Example.git'), False)
        self.assertEqual(commit_report.is_local_repo('git://github.com/UserName/Example.git'), False)

    def test_get_repo_local(self):
        repo = commit_report.get_repo(self.local_repo)
        self.assertIsInstance(repo, Repo)

    def test_create_cache_path(self):
        path = commit_report.create_cache_path(self.remote_repo)
        self.assertEqual(path, self.cache_path)

    def test_repo_remote(self):
        self.assertFalse(os.path.isdir(self.cache_path), msg='Test environment not clean')
        repo = commit_report.get_repo(self.remote_repo)
        # Repo was created
        self.assertTrue(os.path.isdir(self.cache_path))
        self.assertIsInstance(repo, Repo)
        # Run again and confirm refresh was activated
        with patch('commit_report.refresh_repo') as patched:
            commit_report.get_repo(self.remote_repo)
            self.assertEqual(patched.call_count, 1)

    def test_clone_repo(self):
        self.assertFalse(os.path.isdir(self.cache_path), msg='Test environment not clean')
        repo = commit_report.clone_repo(url=self.remote_repo, cache_path=self.cache_path)
        # Repo was created
        self.assertTrue(os.path.isdir(self.cache_path))
        self.assertIsInstance(repo, Repo)

    def test_refresh_repo(self):
        # Need to make sure already have a copy of the repo
        commit_report.get_repo(uri=self.remote_repo)

        # Confirm we are starting clean (no previous fetches)
        self.assertFalse(os.path.exists(self.cache_path + '/.git/FETCH_HEAD'))

        repo = commit_report.refresh_repo(path=self.cache_path)
        self.assertTrue(os.path.exists(self.cache_path + '/.git/FETCH_HEAD'))

    def test_do_it(self):
        self.maxDiff = None
        expected_output = """        06b0bb0d68514272fbe6a4c081b00fae364ccbb5 Tim Laurence         05/02/17 01:48:52 Test 6.1
                                                                                        Test 6.2
        
        794ac3fc424c98fb5ac422ab1ea89b83e065d65c Tim Laurence         05/02/17 01:47:29 
        
        6bf1ec411f5bb159c0cc9e02215ec0d3856344cd Tim Laurence         05/02/17 01:45:07 Test [SWTI-23] 4
        
        b5e0316329d8f546707990deb91ee77353f1ccd4 Tim Laurence         05/02/17 01:44:17 Test 3 [SWTI-23]
        
        99bae718d623d8e2b7a64296b54e70c39699745b Tim Laurence         05/02/17 01:43:10 Test 2
        
        2d0c90f95a728acde5f180f8fef35d41b83d060f Tim Laurence         05/02/17 01:42:02 [SWTI-20] Test 1.1
                                                                                        [SWTI-21] Test 1.2
                                                                                        [SWTI-22] Test 1.3
        
        """

        args = (
            self.remote_repo, self.commit_start, self.commit_end)
        commit_report.do_it(args)
        output = sys.stdout.getvalue()
        self.assertEqual(output.lstrip(), textwrap.dedent(expected_output))

    def test_do_it_links(self):
        self.maxDiff = None
        expected_output = """            06b0bb0d68514272fbe6a4c081b00fae364ccbb5 Tim Laurence         05/02/17 01:48:52 Test 6.1
                                                                                            Test 6.2
            
            794ac3fc424c98fb5ac422ab1ea89b83e065d65c Tim Laurence         05/02/17 01:47:29 
            
            6bf1ec411f5bb159c0cc9e02215ec0d3856344cd Tim Laurence         05/02/17 01:45:07 Test [SWTI-23] 4
            Linked Jira Issues:
            [SWTI-23] : https://jira.com/browse/swti-23
            
            b5e0316329d8f546707990deb91ee77353f1ccd4 Tim Laurence         05/02/17 01:44:17 Test 3 [SWTI-23]
            Linked Jira Issues:
            [SWTI-23] : https://jira.com/browse/swti-23
            
            99bae718d623d8e2b7a64296b54e70c39699745b Tim Laurence         05/02/17 01:43:10 Test 2
            
            2d0c90f95a728acde5f180f8fef35d41b83d060f Tim Laurence         05/02/17 01:42:02 [SWTI-20] Test 1.1
                                                                                            [SWTI-21] Test 1.2
                                                                                            [SWTI-22] Test 1.3
            Linked Jira Issues:
            [SWTI-20] : https://jira.com/browse/swti-20
            [SWTI-21] : https://jira.com/browse/swti-21
            [SWTI-22] : https://jira.com/browse/swti-22

        """

        args = ('--issue-links',
                self.remote_repo, self.commit_start, self.commit_end)
        commit_report.do_it(args)
        output = sys.stdout.getvalue()
        self.assertEqual(output.lstrip(), textwrap.dedent(expected_output))

    def tearDown(self):
        try:
            shutil.rmtree(self.cache_path)
        except FileNotFoundError:
            pass


class TestOutput(unittest.TestCase):
    def setUp(self):
        self.commits = [commit_report.CommitData(id="2d0c90f95a728acde5f180f8fef35d41b83d060{}".format(x),
                                                 author="John Doe",
                                                 timestamp="04/03/17 23:38:25",
                                                 messages='message{}\nmessage'.format(x),
                                                 issues=[commit_report.IssueData(id=x, display=str(x))]
                                                 )
                        for x in range(0, 4)]
        self.maxDiff = None

    def test_human_with_links(self):
        expected_output = """        2d0c90f95a728acde5f180f8fef35d41b83d0600 John Doe             04/03/17 23:38:25 message0
                                                                                        message
        Linked Jira Issues:
        0 : https://jira.com/browse/0

        2d0c90f95a728acde5f180f8fef35d41b83d0601 John Doe             04/03/17 23:38:25 message1
                                                                                        message
        Linked Jira Issues:
        1 : https://jira.com/browse/1

        2d0c90f95a728acde5f180f8fef35d41b83d0602 John Doe             04/03/17 23:38:25 message2
                                                                                        message
        Linked Jira Issues:
        2 : https://jira.com/browse/2

        2d0c90f95a728acde5f180f8fef35d41b83d0603 John Doe             04/03/17 23:38:25 message3
                                                                                        message
        Linked Jira Issues:
        3 : https://jira.com/browse/3
        """

        output = commit_report.format_for_humans(self.commits, include_links=True)
        self.assertEqual(output, textwrap.dedent(expected_output))

    def test_human(self):
        expected_output = """        2d0c90f95a728acde5f180f8fef35d41b83d0600 John Doe             04/03/17 23:38:25 message0
                                                                                        message

        2d0c90f95a728acde5f180f8fef35d41b83d0601 John Doe             04/03/17 23:38:25 message1
                                                                                        message

        2d0c90f95a728acde5f180f8fef35d41b83d0602 John Doe             04/03/17 23:38:25 message2
                                                                                        message

        2d0c90f95a728acde5f180f8fef35d41b83d0603 John Doe             04/03/17 23:38:25 message3
                                                                                        message
        """

        output = commit_report.format_for_humans(self.commits)
        self.assertEqual(output, textwrap.dedent(expected_output))

    def test_json_with_links(self):
        expected_output = [
            {"id": "2d0c90f95a728acde5f180f8fef35d41b83d0601", "author": "John Doe", "timestamp": "04/03/17 23:38:25",
             "messages": "message1\nmessage", "issue_links": ["1 : https://jira.com/browse/1"]}
        ]
        output = commit_report.format_for_json(self.commits[1:2], include_links=True)
        print(output)
        out_obj = json.loads(output)
        self.assertDictEqual(out_obj[0], expected_output[0])

    def test_json(self):
        expected_output = [
            {"id": "2d0c90f95a728acde5f180f8fef35d41b83d0601", "author": "John Doe", "timestamp": "04/03/17 23:38:25",
             "messages": "message1\nmessage"},
        ]
        output = commit_report.format_for_json(self.commits[1:2])
        print(output)
        out_obj = json.loads(output)
        self.assertDictEqual(out_obj[0], expected_output[0])


class TestArgs(unittest.TestCase):
    def test_human_default(self):
        args = ('1', '2', '3')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.formatter, commit_report.format_for_humans)

    def test_human_selected(self):
        args = ('--human', '1', '2', '3')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.formatter, commit_report.format_for_humans)

    def test_json(self):
        args = ('--json', '1', '2', '3')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.formatter, commit_report.format_for_json)

    def test_issue_links_unselected(self):
        args = ('1', '2', '3')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.links, False)

    def test_issue_links_selected(self):
        args = ('--issue-links', '1', '2', '3')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.links, True)

    def test_repo(self):
        args = ('r', 's', 'e')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.repo, 'r')

    def test_start(self):
        args = ('r', 's', 'e')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.start, 's')

    def test_end(self):
        args = ('r', 's', 'e')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.end, 'e')

    def test_template_default(self):
        args = ('r', 's', 'e')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.link_template, commit_report.DEFAULT_LINK_TEMPLATE)

    def test_template_set(self):
        args = ('--link-template', 'test', 'r', 's', 'e')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.link_template, 'test')

    def test_matcher_default(self):
        args = ('r', 's', 'e')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.issue_id_regex, commit_report.DEFAULT_ISSUE_ID_MATCHER)

    def test_matcher_set(self):
        args = ('--issue-matcher', 'test', 'r', 's', 'e')
        result = commit_report.parse_args(args=args)
        self.assertEqual(result.issue_id_regex, 'test')

    def test_arg_error_1(self):
        args = ()
        self.assertRaises(SystemExit, commit_report.parse_args, args)
        output = sys.stdout.getvalue()
        self.assertTrue('show this help message and exit' in output)

    def test_arg_error_2(self):
        args = ('1', '2')
        self.assertRaises(SystemExit, commit_report.parse_args, args)
        output = sys.stdout.getvalue()
        self.assertTrue('show this help message and exit' in output)

    def test_help(self):
        args = ('-h')
        self.assertRaises(SystemExit, commit_report.parse_args, args)
        output = sys.stdout.getvalue()
        self.assertTrue('show this help message and exit' in output)

        args = ('--help')
        self.assertRaises(SystemExit, commit_report.parse_args, args)
        output = sys.stdout.getvalue()
        self.assertTrue('show this help message and exit' in output)


if __name__ == '__main__':
    unittest.main(buffer=True)
