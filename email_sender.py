import smtplib  # Импортируем библиотеку по работе с SMTP

# Добавляем необходимые подклассы - MIME-типы
from email.mime.multipart import MIMEMultipart  # Многокомпонентный объект
from email.mime.text import MIMEText  # Текст/HTML


def email_sender(email_to, message):
    addr_to = email_to
    addr_from = "89096829952@mail.ru"
    password = "Genzr910127"  # пароль от почты addr_from
    msg = MIMEMultipart()  # Создаем сообщение
    msg['From'] = addr_from  # Адресат
    msg['To'] = addr_to  # Получатель
    msg['Subject'] = 'Заказ создан'  # Тема сообщения

    msg.attach(MIMEText(message, 'plain'))  # Добавляем в сообщение текст

    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)  # Создаем объект SMTP
    # server.starttls()             # Начинаем шифрованный обмен по TLS
    server.login(addr_from, password)  # Получаем доступ
    server.send_message(msg)  # Отправляем сообщение
    server.quit()  # Выходим


