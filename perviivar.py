from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import Update
from bs4 import BeautifulSoup
import requests
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData


Base = declarative_base()
DATABASE_URL = 'postgresql://postgres:popa2011@localhost:5432/avito'
# Создание движка SQLAlchemy
engine = create_engine(DATABASE_URL)
# Создание сессии
Session = sessionmaker(bind=engine)

metadata = MetaData()
vacancies_table = Table('vacancies', metadata,
    Column('id', Integer, primary_key=True),
    Column('full_name', String),
    Column('position', String),
    Column('skills', String),
    Column('work_format', String)
)
metadata.create_all(engine)

class Vacancy(Base):
    __tablename__ = 'vacancies'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    position = Column(String)
    skills = Column(String)
    work_format = Column(String)

def load_to_db(data):
    session = Session()
    try:
        with session.begin():
            for item in data:
                # Проверка на существование записи в базе данных
                existing_vacancy = session.query(Vacancy).filter_by(full_name=item['full_name'], position=item['position']).first()
                if existing_vacancy is None:
                    vacancy = Vacancy(
                        full_name=item['full_name'],
                        position=item['position'],
                        skills=item['skills'],
                        work_format=item['work_format']
                    )
                    session.add(vacancy)
                else:
                    # Обновление существующей записи, если необходимо
                    existing_vacancy.skills = item['skills']
                    existing_vacancy.work_format = item['work_format']
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        # Логирование ошибки
        print(f'Ошибка при загрузке данных: {e}')
    finally:
        session.close()
data_to_load = [
    {'full_name': 'Иван Иванов', 'position': 'Разработчик', 'skills': 'Python, SQL', 'work_format': 'Полный день'},
]

# Вызов функции для загрузки данных
load_to_db(data_to_load)

# Функция для парсинга данных с Авито
def parse_avito(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        vacancies = soup.find_all('div', class_='vacancy-class')
        data = []
        for vacancy in vacancies:
            full_name = vacancy.find('div', class_='full-name-class').text.strip()
            position = vacancy.find('div', class_='position-class').text.strip()
            skills = vacancy.find('div', class_='skills-class').text.strip()
            work_format = vacancy.find('div', class_='work-format-class').text.strip()
            data.append({
                'full_name': full_name,
                'position': position,
                'skills': skills,
                'work_format': work_format
            })
        return data
    else:
        print('Ошибка при получении страницы:', response.status_code)
        return None

# Функция для загрузки данных в базу данных
def load_parsed_data(data):
    with engine.connect() as conn:
        for item in data:
            insert_statement = vacancies_table.insert().values(
                full_name=item.get('full_name'),
                position=item.get('position'),
                skills=item.get('skills'),
                work_format=item.get('work_format')
            )
            conn.execute(insert_statement)

# Пример данных для загрузки
data_to_load = [
    {'full_name': 'Иван Иванов', 'position': 'Разработчик', 'skills': 'Python, SQL', 'work_format': 'Полный день'},
]

# Функция для парсинга данных с Авито
url = 'https://www.avito.ru/moskva/vakansii'
def parse_avito(url):
    response = requests.get(url)
# Вызов функции парсинга с передачей URL
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        vacancies = soup.find_all('div', class_='vacancy-class')
        data = []
        for vacancy in vacancies:
            full_name = vacancy.find('div', class_='full-name-class').text.strip()
            position = vacancy.find('div', class_='position-class').text.strip()
            skills = vacancy.find('div', class_='skills-class').text.strip()
            work_format = vacancy.find('div', class_='work-format-class').text.strip()
            data.append({
                'full_name': full_name,
                'position': position,
                'skills': skills,
                'work_format': work_format
            })
        return data
    else:
        print('Ошибка при получении страницы:', response.status_code)
        return None

engine = create_engine('postgresql://postgres:popa2011@localhost:5432/avito')

# Функция для извлечения данных из базы данных
def fetch_from_db():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM vacancies"))
        # Преобразование результатов в список словарей
        keys = result.keys()
        return [dict(zip(keys, row)) for row in result.fetchall()]

# Функция для отправки данных пользователю
def send_data(update, context):
    data = fetch_from_db()
    for item in data:
        message = f"ФИО: {item['full_name']}, Должность: {item['position']}, Навыки: {item['skills']}, Формат работы: {item['work_format']}"
        update.message.reply_text(message)


# Функция для обработки текстовых сообщений
def handle_message(update: Update, context: CallbackContext):
    text_received = update.message.text
    if 'Помоги' in text_received:
        send_data(update, context)
    else:
        update.message.reply_text('Я могу помочь, если вы используете команду /data.')


#фнкц для вывода аналитики
def show_analytics(update: Update, context: CallbackContext):
    # Получение данных о вакансиях
    vacancy_data = context.user_data.get('vacancies', [])
    total_vacancies = len(vacancy_data)
    print(f"Всего вакансий: {total_vacancies}")

    #получение данных о соискателях
    applicant_data = context.user_data.get('applicants', [])
    total_applicants = len(applicant_data)

    # Расчет среднего количества навыков у соискателей
    if total_applicants > 0:  # Проверка, что список  не пуст
        average_skills = sum(len(applicant.get('skills', '').split(',')) for applicant in applicant_data) / total_applicants
        print(f"Среднее количество навыков у соискателей: {average_skills:.2f}")
    else:
        print("Нет данных о соискателях для анализа.")


# Функция для обработки команды /data
def data_command(update, context):
    data = fetch_from_db()
    # Отправка данных пользователю
    for item in data:
        message = f"ФИО: {item['full_name']}, Должность: {item['position']}, Навыки: {item['skills']}, Формат работы: {item['work_format']}"
        update.message.reply_text(message)


# Функция обработчика команды '/start'
def start(update, context):
    update.message.reply_text('Привет! Я бот, который поможет тебе с аналитикой вакансий на Авито. Напишите, какую специальность вы ищете')

# Функция обработчика команды '/analytics'
def analytics_command(update: Update, context: CallbackContext):
    show_analytics(update, context)

# Основная функция, где происходит запуск бота
def main():
    TOKEN = '6823712739:AAEzS1VrGZlK3nrD3b_o_L3Cegl4lptaqEM'

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    #Регистрация обработчиков команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("analytics", analytics_command))
    dp.add_handler(CommandHandler("data", data_command))


    #запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
