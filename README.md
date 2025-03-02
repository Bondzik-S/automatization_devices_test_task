# Automatization Devices Test Task

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Bondzik-S/automatization_devices_test_task.git
   cd automatization-devices-test-task
   ```
   
2. Install dependencies:
   ```bash
   poetry install
   ```

## Running the Project

### With Docker

```bash
  docker-compose up --build
```

### Without Docker

```bash
   cd logging
   poetry run python do_it_yourself.py
```

#### For run tests
```bash
   poetry run pytest 
```


