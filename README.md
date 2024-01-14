<a name="readme-top"></a>
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[!['Black'](https://img.shields.io/badge/code_style-black-black?style=for-the-badge)](https://github.com/psf/black)

<!-- Библиотеки проекта -->
[![telebot](https://img.shields.io/badge/telebot-blue?style=for-the-badge&logo=telegram&logoColor=white)](https://github.com/eternnoir/pyTelegramBotAPI)
[![sqlite3](https://img.shields.io/badge/sqlite3-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)
[![BERT Binary Classifier](https://img.shields.io/badge/BERT%20Binary%20Classifier-red?style=for-the-badge)](#)
[![BERT Multiclass Classifier](https://img.shields.io/badge/BERT%20Multiclass%20Classifier-green?style=for-the-badge)](#)
[![datetime](https://img.shields.io/badge/datetime-blue?style=for-the-badge)](https://docs.python.org/3/library/datetime.html)

<h1 align="center">BioMind chat-bot</h1>

<!-- Содержание -->
<details>
  <summary>Содержание</summary>
  <ol>
    <li>
      <a href="#описание">Описание</a>
      <ul>
        <li><a href="#запуск-чатбота-в-telegram">Запуск чатбота в Telegram</a></li>
      </ul>
    </li>
    <li>
      <a href="#основные-команды-чатбота">Основные команды чатбота</a>
    </li>
  </ol>
</details>

<!-- ОПИСАНИЕ -->
## Описание
BioMind Bot - это чат-бот для Telegram, разработанный для больничной сети "Медси" с целью автоматизации процесса обработки гарантийных писем от страховых компаний. Применяемая нейросеть способна анализировать текстовые документы, выявлять ключевую информацию о медицинских услугах.

Чатбот позволяет вести беседы примерно такого вида:

<img src="chatbot.png" alt="диалог с чатботом в телеграмме" width="350" height="500">

### Запуск чатбота в Telegram

По ссылке можно получить доступ к чатботу : [@biomind_bot](https://t.me/biomind_bot)

Введите команду */hello*, чтобы начать диалог с ботом.

<!-- ОСНОВНЫЕ КОМАНДЫ ЧАТБОТА -->
## Основные команды чатбота
- /help - описание проекта, ссылка на github, выход в главное меню;
- /reset - удаляет все записи в базе данных пользователя и завершает работу;
- /start - выводит кнопки для пользователя (TXT, PDF, DOCX), чтобы пользователь выбрал формат файла, который он хочет обработать.
- /output - выводит всю информацию по обработанным письмам для пользователя. (максимум 3 записи, самая старая запись удаляется)
