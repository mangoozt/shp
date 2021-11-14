import datetime
import json
import subprocess

from homework.models import TestAttempt


def run_test(test_instance: TestAttempt):
    homework = test_instance.homework
    if len(homework.git_repository_url) == 0 or homework.git_repository_url.isspace():
        test_instance.finished = datetime.datetime.now()
        test_instance.passed = False
        test_instance.save()
        return
    try:

        cmd = homework.hometask.test_cmd.replace('{git_repository_url}', homework.git_repository_url)
        finished = subprocess.run(cmd.split(' '),
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, timeout=300)

        test_instance.finished = datetime.datetime.now()
        test_instance.log = finished.stdout.decode()

        try:
            json_log = json.loads(test_instance.log)
            test_instance.passed = json_log['passed']
            test_instance.score = json_log['score']
        except:
            pass

    except TimeoutError:
        test_instance.finished = datetime.datetime.now()
        test_instance.passed = False

    test_instance.save()
