import argparse
import os
import random
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
from django.core.exceptions import MultipleObjectsReturned
from datacenter.models import Chastisement, Commendation, Mark, Schoolkid, Lesson, Subject

COMMENDATIONS = [
    'Молодец!',
    'Отлично!',
    'Ты меня приятно удивил!',
    'Прекрасное начало!',
    'Так держать!',
    'Ты на верном пути!',
    'Здорово!',
    'Это как раз то, что нужно!',
    'С каждым разом у тебя получается всё лучше!',
    'Мы с тобой не зря поработали!',
    'Я вижу, как ты стараешься!',
    'На Девмане лучшим будешь!',
    'Ты растешь над собой!',
    'Ты многое сделал, я это вижу!',
    'Теперь у тебя точно все получится!'
    'Это просто удивительная работа!',
    'Рожден летать!',
    'Это на высшем уровне!',
    'Блестяще!',
    'Мировой стандарт!'
]


def fix_marks(schoolkid):
    Mark.objects.filter(schoolkid=schoolkid, points__in=[2, 3]).update(points=5)


def remove_chastisements(schoolkid):
    schoolkid_warns = Chastisement.objects.filter(schoolkid=schoolkid)
    schoolkid_warns.delete()


def create_commendation(schoolkid, subject):
    Subject.objects.get(title=subject, year_of_study=schoolkid.year_of_study)
    lessons = Lesson.objects.filter(year_of_study=schoolkid.year_of_study,
                                    group_letter=schoolkid.group_letter,
                                    subject__title=subject).order_by('?')
    for lesson in lessons:
        try:
            schoolkid_commendation = Commendation.objects.get(schoolkid=schoolkid,
                                                              subject__title=lesson.subject,
                                                              created=lesson.date)
        except django.core.exceptions.ObjectDoesNotExist:
            schoolkid_commendation = None
        if not schoolkid_commendation:
            Commendation.objects.create(schoolkid=schoolkid,
                                        text=random.choice(COMMENDATIONS),
                                        teacher=lesson.teacher,
                                        created=lesson.date,
                                        subject=lesson.subject
                                        )
        break


def main():
    parser = argparse.ArgumentParser(description="Скрипт для взлома БД школы")
    parser.add_argument("-n", "--name", default="", help="Ввести ФИО или ФИ", type=str)
    parser.add_argument("-s", "--subject", default="", help="Ввести название предмета", type=str)
    args = parser.parse_args()
    schoolkid_name = args.name
    subject = args.subject
    if not schoolkid_name:
        raise ValueError('Необходимо указать имя')
    try:
        schoolkid = Schoolkid.objects.get(full_name__contains=schoolkid_name)
        fix_marks(schoolkid)
        remove_chastisements(schoolkid)
    except Schoolkid.DoesNotExist:
        print(f'Ученика с именем {schoolkid_name} не существует, либо допущена опечатка')
        sys.exit(1)
    except Schoolkid.MultipleObjectsReturned:
        print(f"По запросу {schoolkid_name} найдено несколько учеников,"
              f"уточните ФИО")
        sys.exit(1)
    if not subject:
        raise ValueError('Необходимо указать предмет')
    try:
        create_commendation(schoolkid, subject)
    except Subject.ObjectDoesNotExist:
        print(f"Не найдено предмета по запросу {subject}, либо допущена опечатка")
        sys.exit(1)
    except Schoolkid.MultipleObjectsReturned:
        print(f"По запросу {schoolkid_name} найдено несколько учеников,"
              f"уточните ФИО")
        sys.exit(1)


if __name__ == '__main__':
    main()
