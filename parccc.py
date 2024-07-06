import requests
from bs4 import BeautifulSoup
import psycopg2
import telebot

telegram_token = '7211000175:AAH96nPs3z7KthCSarnqs1DtPz_R2J-9q1A'
bot = telebot.TeleBot(telegram_token)


def initialize_db():
    # Создаем соединение с базой данных
    con = psycopg2.connect(
        dbname="vacancies",
        user="postgres",
        password="popa2011",  
        host="localhost",
        port=5432
    )
    cur = con.cursor()

    # Создание таблицы applicants
    cur.execute("""
    CREATE TABLE IF NOT EXISTS applicants (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        vacancy_id INT,
        application_date DATE,
        speciality VARCHAR(100)
    )
    """)

    # Вставка данных о соискателе
    cur.execute("""
    INSERT INTO applicants (name, email, vacancy_id, application_date, speciality) VALUES
    ('Иван Иванов', 'ivanov@example.com', 1, '2024-07-06', 'Инженер'),
    ('Мария Петрова', 'petrova@example.com', 2, '2024-07-06', 'Аналитик'),
    ('Алексей Смирнов', 'smirnov@example.com', 3, '2024-07-06', 'Разработчик')
    """)


    con.commit()                                            #фиксируе изменения в базе данных
    con.close()                               # Закрываем соединение с базой данных

def fetch_vacancies(url, specialty):
    # Создаем соединение с базой данных
    con = psycopg2.connect(
        dbname="vacancies",
        user="postgres",
        password="popa2011",  
        host="localhost",
        port=5432
    )
    cur = con.cursor()

    # Получаем HTML-код страницы
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    all_vacancy = soup.find_all("div", class_="vacancies-section__item")

    vacancies_counter = 0  # Счетчик для подсчета вакансий

    # Перебираем все элементы с вакансиями
    for vacancy in all_vacancy:
        vacancy_name = vacancy.find("span", class_="vacancies-section__item-link-name").text.strip()
        vacancy_link = "https://career.avito.com" + vacancy.find("a", class_="vacancies-section__item-link").get("href")
        info = vacancy.find("span", class_="vacancies-section__item-format").text.strip() if vacancy.find("span", class_="vacancies-section__item-format") else ""
        location = vacancy.find("span", class_="vacancies-section__item-city").text.strip() if vacancy.find("span", class_="vacancies-section__item-city") else ""

        # Проверяем соответствует ли вакансия запросу специальности
        if specialty.lower() in vacancy_name.lower():
            # Вставляем данные в таблицу PostgreSQL
            cur.execute(
                "INSERT INTO vacancies (name, link, info, location) VALUES (%s, %s, %s, %s)",
                (vacancy_name, vacancy_link, info, location)
            )
            vacancies_counter += 1  #увеличиваю счетчик вакансий

    # Получаем количество соискателей из таблицы applicants
    cur.execute("SELECT COUNT(*) FROM applicants WHERE specialty = %s", (specialty,))
    applicants_counter = cur.fetchone()[0]

    con.commit()                                #фиксация изменений в базе данных
    con.close()                                # Закрываем соединение с базой данных

    return vacancies_counter, applicants_counter    # Возвращаем количество найденных вакансий и соискателей


# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Введите интересующую вас специальность:")

# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def send_vacancies(message):
    specialty = message.text
    vacancies_url = 'https://career.avito.com/vacancies/'
    found_vacancies, found_applicants = fetch_vacancies(vacancies_url, specialty)
    response_message = f"Найдено вакансий по специальности '{specialty}': {found_vacancies}\n"
    response_message += f"Количество соискателей по специальности '{specialty}': {found_applicants}"
    bot.send_message(message.chat.id, response_message)

# Запуск бота
bot.polling(none_stop=True)

# Пример использования функции с запросом специальности
# specialty = input("Введите интересующую вас специальность: ")
# vacancies_url = 'https://career.avito.com/vacancies/'
# found_vacancies, found_applicants = fetch_vacancies(vacancies_url, specialty)
# print(f"Найдено вакансий по специальности '{specialty}': {found_vacancies}")
# print(f"Количество соискателей по специальности '{specialty}': {found_applicants}")













