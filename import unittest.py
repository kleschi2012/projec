import unittest
from parccc import fetch_vacancies


class TestFetchVacancies(unittest.TestCase):
    def test_fetch_vacancies(self):
        #URL для тестирования
        test_url = 'https://career.avito.com/vacancies/test'
        test_specialty = 'Инженер'
        
                                                                                         # Вызываем функцию с тестовыми данными
        vacancies_counter, applicants_counter = fetch_vacancies(test_url, test_specialty)
        
                                                                                    # Проверяем, что функция возвращает кортеж из двух элементов
        self.assertIsInstance(vacancies_counter, int)
        self.assertIsInstance(applicants_counter, int)
        
                                                                                  # Проверяем, что счетчики не отрицательные
        self.assertGreaterEqual(vacancies_counter, 0)
        self.assertGreaterEqual(applicants_counter, 0)

       

if __name__ == '__main__':
    unittest.main()
