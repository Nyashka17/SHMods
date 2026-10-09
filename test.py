# meta developer: @SH_Mods
from .. import loader


@loader.module("RichDemo")
class RichDemoMod(loader.Module):
    """Тестовый модуль: все теги и стили Rich HTML (справочник)

    Команды демонстрируют каждую категорю Rich HTML:
    форматирование текста, ссылки, эмодзи/время, заголовки, списки,
    цитаты, таблицы, медиа, коллаж/карта, формулы, кнопки и стили.
    """

    strings = {
        "name": "RichDemo",
    }

    async def _rich(self, message, text, reply_markup=None, **kwargs):
        return await self.inline.form(
            text=text,
            message=message,
            rich=True,
            reply_markup=reply_markup or [],
            **kwargs,
        )

    async def _on_check(self, call):
        await call.answer("✅ Принято!")
        await call.edit("<b>✅ Подтверждено.</b>")

    async def _on_fail(self, call):
        await call.answer("⚠️ Не удалось подтвердить")

    async def _on_kb(self, call):
        await call.answer("Кнопка работает")

    async def formatcmd(self, message):
        """Текст: b/strong, i/em, u/ins, s/strike/del, code, mark, sub, sup, tg-spoiler, br"""
        await self._rich(
            message,
            (
                "<h1>Оформление текста</h1>"
                "<p>"
                "<b>Жирный</b> или <strong>strong</strong> · "
                "<i>Курсив</i> или <em>em</em> · "
                "<u>Подчёрк</u> или <ins>ins</ins>"
                "</p>"
                "<p>"
                "<s>Старое</s> <strike>strike</strike> <del>del</del> · "
                "<code>.help</code> · "
                "<mark>Выделение маркером</mark> · "
                "H<sub>2</sub>O и м<sup>2</sup> · "
                "<tg-spoiler>Скрытый ответ: 42</tg-spoiler>"
                "<br/>Явный перенос <br/> через br"
                "</p>"
            ),
        )

    async def linkscmd(self, message):
        """Ссылки, якоря, сноски: a href, a name, tg-reference"""
        await self._rich(
            message,
            (
                "<h1>Ссылки, якоря и сноски</h1>"
                "<p>"
                '<a href="https://example.com/guide">Открыть руководство</a> · '
                '<a href="mailto:help@example.com">Написать в поддержку</a> · '
                '<a href="tel:+12025550123">Позвонить</a>'
                "</p>"
                '<p><a href="tg://user?id=1714120111">Упоминание пользователя</a></p>'
                '<a name="setup"></a>'
                "<h2>Настройка</h2>"
                "<p>Содержимое раздела. "
                '<a href="#setup">К настройке</a> · '
                '<a href="#term">Что такое Rich?</a>.</p>'
                '<tg-reference name="term">Rich — структурированное сообщение.</tg-reference>'
            ),
        )

    async def emojicmd(self, message):
        """Кастомные эмодзи и время: tg-emoji, tg-time"""
        await self._rich(
            message,
            (
                "<h1>Эмодзи и время</h1>"
                '<p><tg-emoji emoji-id="5267003499861810620">✨</tg-emoji> Обновление готово</p>'
                '<p><img src="tg://emoji?id=5267003499861810620" alt="✨"/> Альтернативная форма</p>'
                '<p>Начало: <tg-time unix="1800000000" format="wDt">Дата встречи</tg-time>.</p>'
                '<p>До встречи: <tg-time unix="1800000000" format="r">Относительное время</tg-time>.</p>'
            ),
        )

    async def headerscmd(self, message):
        """Заголовки, абзацы, код и разделители: h1-h6, p, pre, code, footer, hr"""
        await self._rich(
            message,
            (
                "<h1>Руководство</h1>"
                "<h2>Установка</h2>"
                "<h3>Настройка</h3>"
                "<h4>Параметры</h4>"
                "<h5>Дополнения</h5>"
                "<h6>Мелкие детали</h6>"
                "<p>Основной текст с <b>выделением</b>.</p>"
                "<pre>Строка с пробелами\n    строка с отступом</pre>"
                '<pre><code class="language-python">for number in range(3):\n'
                "    print(number)</code></pre>"
                "<hr/>"
                "<footer>Версия руководства: 1.0</footer>"
            ),
        )

    async def listscmd(self, message):
        """Списки и чек-листы: ul, ol, li, input checkbox"""
        await self._rich(
            message,
            (
                "<h1>Списки и чек-листы</h1>"
                "<ul>"
                "<li>Установить зависимости</li>"
                "<li>Запустить приложение</li>"
                "</ul>"
                '<ol start="3" type="1">'
                "<li>Третий шаг</li>"
                '<li value="7">Седьмой шаг</li>'
                '<li type="i">Пункт с римским номером</li>'
                "</ol>"
                '<ol start="3" type="a" reversed>'
                "<li>Первый по порядку вывода</li>"
                "<li>Следующий</li>"
                "</ol>"
                "<ul>"
                '<li><input type="checkbox" checked>Файл создан</li>'
                '<li><input type="checkbox">Файл проверен</li>'
                "</ul>"
            ),
        )

    async def quotescmd(self, message):
        """Цитаты и раскрывающиеся блоки: blockquote, aside, cite, details, summary"""
        await self._rich(
            message,
            (
                "<h1>Цитаты и раскрывающиеся блоки</h1>"
                "<blockquote>Сначала проверь входные данные.<br/>"
                "Затем обрабатывай их.<cite>Заметки разработчика</cite></blockquote>"
                "<blockquote expandable>Длинная цитата.<br/>"
                "Её продолжение.<br/>Завершение.</blockquote>"
                "<aside>Самая важная мысль раздела.<cite>Редактор</cite></aside>"
                "<details>"
                "<summary>Показать подробности</summary>"
                "<p>Здесь можно разместить несколько блоков.</p>"
                "<ul><li>Первый пункт</li><li>Второй пункт</li></ul>"
                "</details>"
                "<details open>"
                "<summary>Сразу раскрытый блок</summary>"
                "<p>Содержимое видно при открытии сообщения.</p>"
                "</details>"
            ),
        )

    async def tablecmd(self, message):
        """Таблицы: table, caption, tr, th, td, colspan, rowspan, align, valign"""
        await self._rich(
            message,
            (
                "<h1>Таблицы</h1>"
                '<table bordered striped compact>'
                "<caption>Состояние модулей</caption>"
                "<tr><th>Модуль</th><th>Состояние</th><th>Время</th></tr>"
                '<tr><td rowspan="2" valign="middle">Загрузчик</td>'
                "<td>Запуск</td><td align=\"right\">2 с</td></tr>"
                "<tr><td>Проверка</td><td align=\"right\">1 с</td></tr>"
                '<tr><td colspan="2" align="center"><b>Итого</b></td>'
                "<td align=\"right\">3 с</td></tr>"
                "</table>"
            ),
        )

    async def mediacmd(self, message):
        """Медиа: img, video, audio, tg-document, figure, figcaption, tg-spoiler"""
        await self._rich(
            message,
            (
                "<h1>Медиа</h1>"
                '<img src="https://example.com/photo.jpg"/>'
                '<video src="https://example.com/clip.mp4"></video>'
                '<video src="https://example.com/animation.gif"></video>'
                '<audio src="https://example.com/music.mp3"></audio>'
                '<tg-document src="https://example.com/manual.pdf"></tg-document>'
                "<figure>"
                '<img src="https://example.com/screen.jpg" tg-spoiler/>'
                "<figcaption>Результат работы<cite>Автор снимка</cite></figcaption>"
                "</figure>"
                "<figure>"
                '<video src="https://example.com/demo.mp4" tg-spoiler></video>'
                "<figcaption>Демонстрация</figcaption>"
                "</figure>"
            ),
        )

    async def collagecmd(self, message):
        """Коллаж, слайд-шоу и карта: tg-collage, tg-slideshow, tg-map"""
        await self._rich(
            message,
            (
                "<h1>Коллаж, слайд-шоу и карта</h1>"
                "<tg-collage>"
                '<img src="https://example.com/one.jpg"/>'
                '<img src="https://example.com/two.jpg"/>'
                "<figcaption>Два варианта оформления</figcaption>"
                "</tg-collage>"
                "<tg-slideshow>"
                '<img src="https://example.com/start.jpg"/>'
                '<video src="https://example.com/process.mp4"></video>'
                "<figcaption>Ход работы<cite>Команда проекта</cite></figcaption>"
                "</tg-slideshow>"
                "<figure>"
                '<tg-map lat="55.75" long="37.62" zoom="12"/>'
                "<figcaption>Точка на карте</figcaption>"
                "</figure>"
            ),
        )

    async def mathcmd(self, message):
        """Математические формулы: tg-math, tg-math-block (LaTeX)"""
        await self._rich(
            message,
            (
                "<h1>Математические формулы</h1>"
                "<p>Корни уравнения: "
                r'<tg-math>x_{1,2} = \frac{-b \pm \sqrt{b^2-4ac}}{2a}</tg-math>.</p>'
                r'<tg-math-block>\sum_{k=1}^{n} k = \frac{n(n+1)}{2}</tg-math-block>'
            ),
        )

    async def buttonscmd(self, message):
        """Rich-кнопки во тексте: tg-button ref + стили primary/success/danger/link"""
        await self._rich(
            message,
            (
                "<h1>Rich-кнопки</h1>"
                "<p>Кнопки внутри текста — "
                '<tg-button ref="guide">Руководство</tg-button>, '
                '<tg-button ref="check">Проверить</tg-button>, '
                '<tg-button ref="fail">Ошибка</tg-button>, '
                '<tg-button ref="stat">Статус</tg-button>.</p>'
            ),
            reply_markup=[
                [
                    {
                        "text": "Руководство",
                        "ref": "guide",
                        "url": "https://example.com/guide",
                        "style": "primary",
                    }
                ],
                [
                    {
                        "text": "Проверить",
                        "ref": "check",
                        "callback": self._on_check,
                        "style": "success",
                    }
                ],
                [
                    {
                        "text": "Ошибка",
                        "ref": "fail",
                        "callback": self._on_fail,
                        "style": "danger",
                    }
                ],
                [
                    {
                        "text": "Статус",
                        "ref": "stat",
                        "url": "https://example.com/status",
                        "style": "link",
                    }
                ],
            ],
            ttl=60 * 30,
        )

    async def keycmd(self, message):
        """Клавиатура под сообщением: url, callback, input, data"""
        await self._rich(
            message,
            "<h1>Клавиатура</h1><p>Обычная inline-клавиатура под rich-сообщением.</p>",
            reply_markup=[
                [{"text": "🌐 Сайт", "url": "https://example.com"}],
                [{"text": "✅ Подтвердить", "callback": self._on_kb}],
                [{"text": "🔍 Искать", "input": "подставит запрос в чат"}],
                [{"text": "📋 Данные", "data": "raw_callback_payload"}],
            ],
            force_me=True,
        )

    async def fullcmd(self, message):
        """Полный пример: все основные блоки вместе"""
        await self._rich(
            message,
            (
                '<a name="top"></a>'
                "<h1>Отчёт о проверке</h1>"
                "<p><b>Статус:</b> <mark>готово</mark><br/>"
                "Версия: <code>1.0</code></p>"
                '<p><a href="#details">Перейти к результатам</a></p>'
                "<h2>Выполнено</h2>"
                "<ul>"
                '<li><input type="checkbox" checked>Проверены настройки</li>'
                '<li><input type="checkbox" checked>Собрана сводка</li>'
                '<li><input type="checkbox">Проверить результат вручную</li>'
                "</ul>"
                '<a name="details"></a>'
                '<table bordered striped compact>'
                "<caption>Результаты</caption>"
                "<tr><th>Проверка</th><th>Результат</th></tr>"
                "<tr><td>Конфигурация</td><td><b>OK</b></td></tr>"
                "<tr><td>Файлы</td><td><b>OK</b></td></tr>"
                "</table>"
                "<details>"
                "<summary>Технические подробности</summary>"
                "<p>Показана учебная сводка.</p>"
                '<pre><code class="language-python">result = {"ok": True}\n'
                "print(result)</code></pre>"
                "</details>"
                "<blockquote>Перед публикацией прочитай результат."
                "<cite>Правило проекта</cite></blockquote>"
                "<p>Оценка времени: <tg-math>t = n / v</tg-math>.</p>"
                '<p>Примечание <a href="#note">[1]</a>.</p>'
                '<tg-reference name="note">'
                "Значения в отчёте приведены для примера.</tg-reference>"
                "<hr/>"
                '<footer><a href="#top">К началу</a> · Конец отчёта</footer>'
            ),
        )
