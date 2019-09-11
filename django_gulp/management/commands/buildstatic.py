import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):
    """Wrap gulp"""

    def handle(self, *args, **options):

        popen_kwargs = {
            'shell': True,
            'stdin': subprocess.PIPE,
            'stdout': self.stdout._out,
            'stderr': self.stderr._out
        }

        # HACK: This command is executed without node_modules in the PATH
        # when it's executed from Heroku... Ideally we wouldn't need any
        # Heroku-specific code for this to work.
        if os.path.exists('/app/requirements.txt'):
            popen_kwargs['env'] = {
                'PATH': (os.environ['PATH'] +
                         ':/app/node_modules/.bin' +
                         ':/app/.heroku/node/bin')
            }

        gulp_cwd = getattr(settings, 'GULP_CWD', os.getcwd())
        gulp_command = getattr(
            settings, 'GULP_PRODUCTION_COMMAND', 'gulp build --cwd %s --production' % gulp_cwd)
        try:
            subprocess.check_call(gulp_command, **popen_kwargs)
        except subprocess.CalledProcessError as e:
            raise CommandError(e)
