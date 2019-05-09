import argparse
import sys
import traceback

import yaml

from rdm.collect import collect_from_files
from rdm.doctor import check_data_files
from rdm.hooks import install_hooks
from rdm.init import init
from rdm.pull import pull_from_project_manager
from rdm.render import render_template_to_file
from rdm.tex import yaml_gfm_to_tex
from rdm.translate import translate_test_results, XML_FORMATS
from rdm.util import context_from_data_files, print_error


def main():
    try:
        exit_code = cli(sys.argv[1:])
        sys.exit(exit_code)
    except Exception:
        print_error(traceback.format_exc())
        sys.exit(1)


def cli(raw_arguments):
    exit_code = 0
    args = parse_arguments(raw_arguments)
    if args.command is None:
        parse_arguments(['-h'])
    elif args.command == 'render':
        context = context_from_data_files(args.data_files)
        render_template_to_file(args.template, context, sys.stdout)
    elif args.command == 'tex':
        context = context_from_data_files(args.data_files)
        yaml_gfm_to_tex(args.input, context, sys.stdout)
    elif args.command == 'init':
        init(args.output)
    elif args.command == 'pull':
        cache_dir = args.cache
        pull_from_project_manager(args.system_yml, cache_dir)
    elif args.command == 'hooks':
        install_hooks(args.dest)
    elif args.command == 'collect':
        snippets = collect_from_files(args.files)
        yaml.dump(snippets, sys.stdout)
    elif args.command == 'doctor':
        errors = check_data_files()
        if errors:
            exit_code = 1
    elif args.command == 'translate':
        translate_test_results(args.format, args.input, args.output)
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
    pull_cache_help = 'Directory to load/save cached request data from backend'
    pull_parser.add_argument('-c', '--cache', default=None, help=pull_cache_help)

    hooks_help = 'install githooks in current repository'
    hooks_parser = subparsers.add_parser('hooks', help=hooks_help)
    hooks_parser.add_argument('dest', nargs='?', help='Path to where hooks are to be saved.')

    collect_help = 'collect documentation snippets into a yaml file'
    collect_parser = subparsers.add_parser('collect', help=collect_help)
    collect_parser.add_argument('files', nargs='*')

    doctor_help = 'check your regulatory docs for potential problems'
    subparsers.add_parser('doctor', help=doctor_help)

    translate_help = 'translate test output to create test result yaml file'
    translate_parser = subparsers.add_parser('translate', help=translate_help)
    translate_parser.add_argument('format', choices=XML_FORMATS)
    translate_parser.add_argument('input')
    translate_parser.add_argument('output')

    return parser.parse_args(arguments)


if __name__ == '__main__':
    main()
