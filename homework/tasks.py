import datetime
import json
import subprocess

from homework.models import TestAttempt


def run_test(test_instance: TestAttempt):
    homework = test_instance.homework
    try:
        finished = subprocess.run(homework.hometask.test_cmd.split(' '),
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, timeout=35)

        test_instance.finished = datetime.datetime.now()
        test_instance.log = finished.stdout
        if finished.returncode == 0:
            test_instance.passed = True if finished.returncode == 0 else False

        try:
            test_instance.score = json.loads(finished.stdout)['score']
        except:
            pass

    except TimeoutError:
        test_instance.finished = datetime.datetime.now()
        test_instance.passed = False

    test_instance.save()
