#!/usr/bin/python

from argparse import ArgumentParser
from github import Github
from subprocess import call

class Gitshlub(object):
    def __init__(self, user=None, password=None):
        if user and password:
            self._github = Github(user, password)
        else:
            self._github = Github()

    def do_superclone(self, args):
        # search Github for repo
        if not args.query:
            args.query = raw_input('Repo to search for: ')
        repos = self._github.search_repositories(args.query)
        if repos.totalCount == 0:
            print('Search returned no results, exiting.')
            return

        # select repo
        i = 0
        for repo in repos:
            print '%d: %s' % (i, repo.full_name)
            i += 1
            if i == repos.totalCount:
                raw = raw_input('Enter a number to select a repo or any '
                                'other key to cancel: ')
            elif i % 10 == 0:
                raw = raw_input('Press Enter for more results, a number to '
                                'select a repo or any other key to cancel: ')
            else:
                continue
            if raw == '':
                continue
            try:
                repo = repos[int(raw)]
                break
            except ValueError, IndexError:
                print 'Exiting'
                return

        # select URL
        url = 'clone_url'
        if args.git_url:
            url = 'git_url'

        # clone
        if args.dry_run:
            print 'DRY RUN: git clone %s' % getattr(repo, url)
        else:
            call(['git', 'clone', getattr(repo, url)])


if __name__ == '__main__':
    shlub = Gitshlub()

    # top-level parser
    desc = 'Gitshlub is a set of tools for using Github from the command line.'
    parser = ArgumentParser(prog='gitshlub', description=desc)
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='simulate execution of sub-command')
    cmd_parsers = parser.add_subparsers()

    # superclone parser
    superclone_desc = 'Search Github for a repository and clone it.'
    superclone_help = 'search for a repo and clone it'
    superclone_parser = cmd_parsers.add_parser('superclone',
                                               description=superclone_desc,
                                               help=superclone_help)
    superclone_parser.add_argument('query', nargs='?', help='repo to search for')
    superclone_parser.add_argument('-g', '--git-url', action='store_true',
                                   help='use \'git://\' URL to clone')
    superclone_parser.set_defaults(func=shlub.do_superclone)

    # run sub command
    args = parser.parse_args()
    args.func(args)