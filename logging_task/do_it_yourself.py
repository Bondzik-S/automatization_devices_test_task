import time
import os


def parse_log_line(line: str) -> dict[str, str] | None:
    """
    Parses a single log line and returns a dictionary with extracted data if the line is valid.
    The expected format is a message enclosed in quotes and separated by ';' after "> ".

    Required data:
      - handler (position 0) must be "BIG"
      - sensor_id (position 2) – converted to uppercase
      - S_P_1 (position 6)
      - S_P_2 (position 15)
      - state (second-to-last element)
    Returns None if the line is invalid.
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
    except (IndexError, AttributeError):
        return None


def is_ok(entry: dict[str, str]) -> bool:
    """Returns True if the state is '02'."""
    return entry.get("state") == "02"


def is_failed(entry: dict[str, str]) -> bool:
    """Returns True if the state is 'DD'."""
    return entry.get("state") == "DD"


def process_error(sp1: str, sp2: str) -> str:
    """
    Processes an error for entries with state "DD" using S_P_1 and S_P_2 values.

    Algorithm:
      1. Remove the last character from S_P_1 (checksum) and strip the minus sign from S_P_2.
      2. Concatenate the processed strings, pad with zeros on the left if needed,
         and trim to exactly 6 characters.
      3. For each of the three 2-character pairs:
         - Convert the pair to an 8-bit binary string.
         - Check the 5th bit (index 4) and return the corresponding error message based on priority:
             - First pair: "Battery device error"
             - Second pair: "Temperature device error"
             - Third pair: "Threshold central error"
      4. If no flag is set, return "Unknown device error".
    """
    if sp1 == "" or sp2 == "":
        return "Unknown device error"
    sp1_processed = sp1[:-1]
    sp2_processed = sp2.lstrip("-")
    combined = (sp1_processed + sp2_processed).zfill(6)[:6]
    error_types = [
        "Battery device error",
        "Temperature device error",
        "Threshold central error"
    ]
    for i in range(3):
        pair = combined[i * 2 : i * 2 + 2]
        if format(int(pair), "08b")[4] == "1":
            return error_types[i]
    return "Unknown device error"


def process_file(file_path: str) -> tuple[int, int, int, dict[str, str], dict[str, int]] | None:
    """
    Processes a log file and returns statistics:
      - all_devices: count of unique sensors with BIG messages
      - successful_devices: sensors that always sent state "02"
      - failed_devices: sensors that sent state "DD" at least once
      - failed_sensors: dictionary {sensor_id: error_message} for faulty sensors
      - success_messages: dictionary {sensor_id: count} for sensors that always sent "02"
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None

    success_messages = {}
    failed_sensors = {}

    try:
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

    except OSError as e:
        print(f"Error: Unable to read file '{file_path}'. Reason: {e}")
        return None


def print_results(all_devices, successful_devices, failed_devices, failed_sensors, success_messages):
    """Prints the processed statistics in a readable format."""
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
    """
        Entry point of the script.
        Measures execution time, processes the log file, and prints the results.
    """
    start = time.time()
    file_path = "app_2.log"
    results = process_file(file_path)
    print_results(*results)
    print("Optimized version took " + str(time.time() - start) + " seconds.")


if __name__ == '__main__':
    main()
