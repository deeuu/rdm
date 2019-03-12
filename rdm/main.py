#!/usr/bin/env python3
import sys
import traceback
import argparse
import os
import sys
import yaml

from rdm.util import print_error
from rdm.render import render_template
from rdm.tex import yaml_gfm_to_tex
from rdm.init import init
from rdm.pull import pull_from_project_manager
from rdm.hooks import install_hooks
from rdm.collect import collect_from_files
from rdm.util import context_from_data_files
from rdm.doctor import check_data_files


def main(raw_arguments):
    exit_code = 0
    args = parse_arguments(raw_arguments)
    if args.command is None:
        parse_arguments(['-h'])
    elif args.command == 'render':
        context = context_from_data_files(args.data_files)
        render_template(args.template, context, sys.stdout)
    elif args.command == 'tex':
        context = context_from_data_files(args.data_files)
        yaml_gfm_to_tex(args.input, context, sys.stdout)
    elif args.command == 'init':
        init(args.output)
    elif args.command == 'pull':
        output_dir = args.output or os.path.dirname(args.system_yml)
        pull_from_project_manager(args.system_yml, output_dir)
    elif args.command == 'hooks':
        install_hooks(args.dest)
    elif args.command == 'collect':
        snippets = collect_from_files(args.files)
        yaml.dump(snippets, sys.stdout)
    elif args.command == 'doctor':
        errors = check_data_files()
        if errors:
            exit_code = 1
    return exit_code


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(prog='rdm')
    subparsers = parser.add_subparsers(dest='command', metavar='<command>')

    init_help = 'initialize a set of templates in the output directory'
    init_parser = subparsers.add_parser('init', help=init_help)
    init_parser.add_argument('-o', '--output', default='regulatory')

    render_help = 'render a template using the specified data files'
    render_parser = subparsers.add_parser('render', help=render_help)
    render_parser.add_argument('template')
    render_parser.add_argument('data_files', nargs='*')

    tex_help = 'translate a yaml+gfm file into a tex file using pandoc'
    tex_parser = subparsers.add_parser('tex', help=tex_help)
    tex_parser.add_argument('input')
    tex_parser.add_argument('data_files', nargs='*')

    pull_help = 'pull data from the project management tool'
    pull_parser = subparsers.add_parser('pull', help=pull_help)
    pull_parser.add_argument('system_yml', help='Path to project `system.yml` file.')
    pull_output_help = 'Directory to output data files. Defaults to same location of system_yml'
    pull_parser.add_argument('-o', '--output', default=None, help=pull_output_help)

    hooks_help = 'install githooks in current repository'
    hooks_parser = subparsers.add_parser('hooks', help=hooks_help)
    hooks_parser.add_argument('dest', nargs='?', help='Path to where hooks are to be saved.')

    collect_help = 'collect documentation snippets into a yaml file'
    collect_parser = subparsers.add_parser('collect', help=collect_help)
    collect_parser.add_argument('files', nargs='*')

    doctor_help = 'check your regulatory docs for potential problems'
    subparsers.add_parser('doctor', help=doctor_help)

    return parser.parse_args(arguments)


if __name__ == '__main__':
    try:
        exit_code = main(sys.argv[1:])
        sys.exit(exit_code)
    except Exception:
        print_error(traceback.format_exc())
        sys.exit(1)
