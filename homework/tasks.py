import datetime
import json
import subprocess
import tempfile

from homework.models import TestAttempt


def call_subprocess(m):
    def f(*args, **kwargs):
        cp = m(*args, **kwargs)
        return cp.returncode == 0, cp.stderr

    return f


@call_subprocess
def clone_repository(url, directory):
    return subprocess.run(['git', 'clone', url, directory], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          stdin=subprocess.PIPE, timeout=35)


def run_test(test_instance: TestAttempt):
    with tempfile.TemporaryDirectory() as tmpdir:
        homework = test_instance.homework
        if len(homework.git_repository_url) == 0 or homework.git_repository_url.isspace():
            test_instance.finished = datetime.datetime.now()
            test_instance.passed = False
            test_instance.save()
            return
        try:
            cloned, clone_err = clone_repository(homework.git_repository_url, tmpdir)
            if not cloned:
                result = {'passed': False, 'tests': []}
                result['tests'].append(
                    {"name": "Clone repository", "passed": False, "safe": True, "message": clone_err.decode()})
                test_instance.finished = datetime.datetime.now()
                test_instance.log = result
            else:
                cmd = homework.hometask.test_cmd.format(git_repository_url=homework.git_repository_url,
                                                        local_repository_dir=tmpdir)

                finished = subprocess.run(cmd.split(' '),
                                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE,
                                          timeout=300)

                test_instance.finished = datetime.datetime.now()
                test_instance.log = finished.stdout.decode()

                try:
                    json_log = json.loads(test_instance.log)
                    test_instance.passed = json_log['passed']
                    test_instance.score = json_log['score']
                except:
                    pass

        except subprocess.TimeoutExpired:
            test_instance.finished = datetime.datetime.now()
            test_instance.passed = False

        test_instance.save()
