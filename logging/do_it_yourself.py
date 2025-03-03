import time


def parse_log_line(line):
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
    except:
        return None


def is_ok(entry):
    """Returns True if the state is '02'."""
    return entry.get("state") == "02"


def is_failed(entry):
    """Returns True if the state is 'DD'."""
    return entry.get("state") == "DD"


def process_error(sp1, sp2):
    """
    Processes an error for entries with state "DD" using S_P_1 and S_P_2 values.

    Algorithm:
      1. Remove the last character from S_P_1 (checksum) and strip the minus sign from S_P_2.
      2. Concatenate the processed strings. If the length is less than 6, pad with zeros on the left;
         if longer, trim to 6 characters.
      3. Split the string into three pairs (2 characters each).
      4. Convert each pair into an 8-bit binary representation.
      5. Extract the 5th bit (index 4) from each binary number.
      6. Return only one error message based on priority:
           - If the first bit = '1' → "Battery device error"
           - Otherwise, if the second bit = '1' → "Temperature device error"
           - Otherwise, if the third bit = '1' → "Threshold central error"
           - If no flags are set → "Unknown device error"
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
    Processes a log file and returns statistics:
      - all_devices: count of unique sensors with BIG messages
      - successful_devices: sensors that always sent state "02"
      - failed_devices: sensors that sent state "DD" at least once
      - failed_sensors: dictionary {sensor_id: error_message} for faulty sensors
      - success_messages: dictionary {sensor_id: count} for sensors that always sent "02"
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
