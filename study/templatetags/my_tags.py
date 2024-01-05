from django import template

register = template.Library()


@register.simple_tag
def media_path(val: str) -> str:
    """ Принимает имя медиафайла, возвращает путь к нему """
    if val:
        return f"/media/{val}"
    return "#"


@register.simple_tag
def question_path(test_pk: int, questions_pk: list, index: int) -> str:
    """
    Принимает pk теста, список pk вопросов к этому тесту и номер итерации forloop.counter.
    Если находит вопрос по индексу forloop.counter, то возвращает путь изменению этого вопроса,
    если не находит - возвращает путь к изменению теста этого вопроса
    """
    try:
        return f'/study/question/{questions_pk[index]}/update/'
    except IndexError:
        return f'/study/tests/{test_pk}/update/'
