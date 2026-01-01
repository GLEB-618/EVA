from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_inline_keyboard(buttons: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру.
    
    :param buttons: Список строк кнопок, где каждая кнопка — кортеж (текст, callback_data).
                    Пример: [[("Кнопка 1", "callback_1")], [("Кнопка 2", "callback_2"), ("Кнопка 3", "callback_3")]]
    :return: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=data) for text, data in row]
        for row in buttons
    ])
    return keyboard