import time


def parse_log_line(line):
    """
    Розбирає один рядок логу і повертає словник з даними, якщо рядок валідний.
    Очікується, що після "> " знаходиться частина повідомлення в лапках, розділена ';'.

    Необхідні дані:
      - handler (позиція 0) має бути "BIG"
      - sensor_id (позиція 2) – приводиться до верхнього регістру
      - S_P_1 (позиція 6)
      - S_P_2 (позиція 15)
      - state (передостанній елемент)
    Якщо не все в порядку, повертає None.
    """
    if "> " not in line:
        return None
    try:
        part = line.split("> ", 1)[1].strip().strip("'")
        parts = part.split(";")
        if len(parts) < 18:
            return None
        if parts[0].strip() != "BIG":
            return None
        sensor_id = parts[2].strip().upper()
        sp1 = parts[6].strip()
        sp2 = parts[15].strip()
        state = parts[-2].strip()
        return {"sensor_id": sensor_id, "sp1": sp1, "sp2": sp2, "state": state}
    except:
        return None


def is_ok(entry):
    """Повертає True, якщо стан '02'."""
    return entry.get("state") == "02"


def is_failed(entry):
    """Повертає True, якщо стан 'DD'."""
    return entry.get("state") == "DD"


def process_error(sp1, sp2):
    """
    Обробляє помилку для записів зі станом "DD" за даними S_P_1 і S_P_2.
    Алгоритм:
      1. Видаляємо останній символ з S_P_1 (контрольна сума) та прибираємо мінус з S_P_2.
      2. Конкатенуємо отримані рядки. Якщо довжина менша за 6 – доповнюємо нулями зліва,
         якщо довша – обрізаємо до 6 символів.
      3. Розбиваємо рядок на три пари (по 2 символи).
      4. Перетворюємо кожну пару в 8-бітове двійкове представлення.
      5. З кожного двійкового числа беремо 5-й біт (індекс 4).
      6. Повертаємо лише одну помилку за пріоритетом:
           - Якщо перший біт = '1' → "Battery device error"
           - Інакше, якщо другий біт = '1' → "Temperature device error"
           - Інакше, якщо третій біт = '1' → "Threshold central error"
           - Якщо жоден прапорець не встановлено → "Unknown device error"
    """
    if sp1 == "" or sp2 == "":
        return "Unknown device error"
    sp1_processed = sp1[:-1]
    sp2_processed = sp2.lstrip('-')
    combined = sp1_processed + sp2_processed
    if len(combined) < 6:
        while len(combined) < 6:
            combined = "0" + combined
    elif len(combined) > 6:
        combined = combined[:6]
    pair1 = combined[0:2]
    pair2 = combined[2:4]
    pair3 = combined[4:6]
    b1 = format(int(pair1), '08b')
    b2 = format(int(pair2), '08b')
    b3 = format(int(pair3), '08b')
    bit1 = b1[4]
    bit2 = b2[4]
    bit3 = b3[4]
    if bit1 == '1':
        return "Battery device error"
    elif bit2 == '1':
        return "Temperature device error"
    elif bit3 == '1':
        return "Threshold central error"
    else:
        return "Unknown device error"


def process_file(file_path):
    """
    Обробляє лог-файл і повертає статистику:
      - all_devices: кількість унікальних сенсорів із BIG повідомленнями
      - successful_devices: сенсори, що завжди надсилали "02"
      - failed_devices: сенсори, які хоча б раз надіслали "DD"
      - failed_sensors: словник {sensor_id: error_message} для несправних сенсорів
      - success_messages: словник {sensor_id: count} для сенсорів, що завжди надсилали "02"
    """
    success_messages = {}
    failed_sensors = {}

    with open(file_path, 'r') as f:
        for line in f:
            entry = parse_log_line(line)
            if entry is None:
                continue
            sensor_id = entry["sensor_id"]
            if is_failed(entry):
                if sensor_id not in failed_sensors:
                    error_msg = process_error(entry["sp1"], entry["sp2"])
                    failed_sensors[sensor_id] = error_msg
            elif is_ok(entry):
                if sensor_id not in failed_sensors:
                    if sensor_id in success_messages:
                        success_messages[sensor_id] += 1
                    else:
                        success_messages[sensor_id] = 1

    for sensor in list(failed_sensors.keys()):
        if sensor in success_messages:
            del success_messages[sensor]

    all_devices = len(success_messages) + len(failed_sensors)
    return all_devices, len(success_messages), len(failed_sensors), failed_sensors, success_messages


def print_results(all_devices, successful_devices, failed_devices, failed_sensors, success_messages):
    print("All big messages: " + str(all_devices) + "\n")
    print("Successful big messages: " + str(successful_devices) + "\n")
    print("Failed big messages: " + str(failed_devices) + "\n")
    for sensor_id, error_msg in failed_sensors.items():
        print(sensor_id + ": " + error_msg)
    print("\nSuccess messages count:")
    sorted_success = sorted(success_messages.items(), key=lambda x: x[1], reverse=True)
    for sensor_id, count in sorted_success:
        print(sensor_id + ": " + str(count))


def main():
    start = time.time()
    file_path = "app_2.log"
    results = process_file(file_path)
    print_results(*results)
    print("Optimized version took " + str(time.time() - start) + " seconds.")


if __name__ == '__main__':
    main()
