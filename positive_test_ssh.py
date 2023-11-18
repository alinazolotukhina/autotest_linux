import paramiko
import yaml
import os
import time

# Функция для выполнения команды через SSH и проверки вывода
def ssh_checkout(host, user, passwd, cmd, text, port=22):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=user, password=passwd, port=port)
    stdin, stdout, stderr = client.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    out = (stdout.read() + stderr.read()).decode('utf-8')
    client.close()
    return text in out and exit_code == 0

# Функция для добавления строки статистики в файл
def append_stat_line(config, stat_file_path):
    # Получение времени
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # Получение количества файлов и размера файла
    file_count = len(os.listdir(config['folder_out']))
    file_size = os.path.getsize(config['folder_out'] + '/arx2.7z')

    # Получение статистики загрузки процессора
    with open('/proc/loadavg', 'r') as file:
        load_avg = file.read().strip()

    # Формирование строки статистики
    stat_line = f"{current_time}, {file_count}, {file_size}, {load_avg}\n"

    # Добавление строки в файл статистики
    with open(stat_file_path, 'a') as file:
        file.write(stat_line)
    pass

# Функция для запуска тестовых шагов через SSH
def test_step(config, step_number, cmd, text):
    host = config['ssh_host']
    user = config['ssh_user']
    passwd = config['ssh_password']
    result = ssh_checkout(host, user, passwd, cmd, text)
    assert result, f"test{step_number} FAIL"
    append_stat_line(config, stat_file_path)

# Главная функция для запуска тестов
def run_tests(config_path, stat_file_path):
    # Загрузка конфигурации из файла config.yaml
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Запуск тестовых функций через SSH
    test_step(config, 1, f"cd {config['folder_in']}; 7z a -r ../out/arx2", "Everything is OK")
    test_step(config, 2, f"cd {config['folder_out']}; 7z e arx2.7z -o{config['folder_ext1']} -y", "Everything is OK")
    test_step(config, 3, f"cd {config['folder_out']}; 7z t arx2.7z", "Everything is OK")
    test_step(config, 4, f"cd {config['folder_out']}; 7z u arx2.7z", "Everything is OK")
    test_step(config, 5, f"cd {config['folder_out']}; 7z d arx2.7z -r", "Everything is OK")

# Запуск тестов
config_path = '/home/user/config.yaml'
stat_file_path = '/home/user/stat.txt'
run_tests(config_path, stat_file_path)
