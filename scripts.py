import argparse
import logging
import os
import random
import sys

import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from datacenter.models import Chastisement, Commendation, Mark, Schoolkid, Lesson, Subject


def fix_marks(schoolkid):
    Mark.objects.filter(schoolkid=schoolkid, points__in=[2, 3]).update(points=5)


def remove_chastisements(schoolkid):
    child_warns = Chastisement.objects.filter(schoolkid__full_name__contains=schoolkid)
    child_warns.delete()


def create_commendation(schoolkid, lessons):
    commendations = [
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
    for lesson in lessons:
        try:
            schoolkid_commendation = Commendation.objects.get(schoolkid=schoolkid,
                                                              subject__title=lesson.subject,
                                                              created=lesson.date)
        except django.core.exceptions.ObjectDoesNotExist:
            schoolkid_commendation = None
        if not schoolkid_commendation:
            Commendation.objects.create(schoolkid=schoolkid,
                                        text=random.choice(commendations),
                                        teacher=lesson.teacher,
                                        created=lesson.date,
                                        subject=lesson.subject
                                        )
        break


def main():
    parser = argparse.ArgumentParser(description="Скрипт для взлома БД школы")
    parser.add_argument("-n", "--name", default="", help="Введите ФИО или ФИ", type=str, action='store')
    parser.add_argument("-s", "--subject", default="", help="Введите название предмета")
    args = parser.parse_args()
    schoolkid_name = args.name
    subject = args.subject
    if not schoolkid_name:
        raise ValueError(' Необходимо указать имя')
    try:
        schoolkid = Schoolkid.objects.get(full_name__contains=schoolkid_name)
        fix_marks(schoolkid)
        remove_chastisements(schoolkid)
    except ObjectDoesNotExist:
        print(f'Ученика с именем {schoolkid_name} не существует, либо допущена опечатка')
        sys.exit()
    except MultipleObjectsReturned:
        logging.error(f" По запросу {schoolkid_name} найдено несколько учеников,"
                      f"уточните ФИО")
        sys.exit()
    if not subject:
        raise ValueError('Необходимо указать предмет')
    try:
        schoolkid = Schoolkid.objects.get(full_name__contains=schoolkid_name)
        Subject.objects.get(title=subject, year_of_study=schoolkid.year_of_study)
        subjects = Lesson.objects.filter(year_of_study=schoolkid.year_of_study,
                                         group_letter=schoolkid.group_letter,
                                         subject__title=subject).order_by('?')
        create_commendation(schoolkid, subjects)
    except ObjectDoesNotExist:
        logging.error(f' Не найдено предмета по запросу {subject}, либо допущена опечатка')
        sys.exit()
    except MultipleObjectsReturned:
        logging.error(f" По запросу {schoolkid_name} найдено несколько учеников,"
                      f"уточните ФИО")
        sys.exit()


if __name__ == '__main__':
    main()
