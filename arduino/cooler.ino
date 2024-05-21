#include <EEPROM.h>

#include "LiquidCrystal_I2C.h"

// CONSTANTS
#define LCD_COLS 16
#define LCD_ROWS 2
#define ANALOGPIN A0
#define TEMPMASIZE 220
#define MAXMODEPIN 10
#define MINMODEPIN 11
#define INCREASETEMPPIN 9
#define DECREASETEMPPIN 12
#define MINTEMPADDR 1016  // 1016-1020
#define MAXTEMPADDR 1020  // 1020-1024
#define PUMPPIN 8
#define MOTORPIN 7
#define IDLEMILLIS 5000
#define DEBOUNCEMILLIS 300
#define TEMPSTEP .1


// GLOBALS
LiquidCrystal_I2C lcd(0x27, LCD_COLS, LCD_ROWS);
int temp_index = 0;
float temp_array[TEMPMASIZE];
float temp;
String mode = "auto";
float min_temperature = 25.0;
float max_temperature = 26.5;
String manifest_line1 = "";
String manifest_line2 = "";
bool cooler_state = false;


void setup() {
  // serial
  Serial.begin(115200);
  Serial.println("Init...");

  // lcd
  lcd.init();
  lcd.clear();
  lcd.backlight();
  Serial.println("lcd is OK");

  // adc
  analogReference(EXTERNAL);
  for (int i = 0; i < TEMPMASIZE; i++) {
    read_temperature();
    delay(1);
  }

  // setting buttons
  pinMode(MAXMODEPIN, INPUT);
  digitalWrite(MAXMODEPIN, HIGH);
  pinMode(MINMODEPIN, INPUT);
  digitalWrite(MINMODEPIN, HIGH);
  pinMode(INCREASETEMPPIN, INPUT);
  digitalWrite(INCREASETEMPPIN, HIGH);
  pinMode(DECREASETEMPPIN, INPUT);
  digitalWrite(DECREASETEMPPIN, HIGH);

  // setting pump and morot pins
  pinMode(PUMPPIN, OUTPUT);
  pinMode(MOTORPIN, OUTPUT);

  // recover constants
  // write_thresholds();
  read_thresholds();

  // initialize variables
  if (temp > max_temperature) {
    cooler_state = true;
    digitalWrite(MOTORPIN, LOW);
    delay(10);
    digitalWrite(PUMPPIN, LOW);
  }
  else {
    digitalWrite(MOTORPIN, HIGH);
    digitalWrite(PUMPPIN, HIGH);
  }
}

void loop() {
  // Update temperature
  read_temperature();
  // Update info on lcd
  update_manifests();
  write_manifests();
  // Check mode
  check_mode();
  //Go to set mode min/max is pressed; This mode is blocking
  if (mode != "auto") {
    set_thresholds();
  }
  // Otherwise control cooler automatically
  if (cooler_state) {
    if (temp < min_temperature) {
      digitalWrite(MOTORPIN, HIGH);
      delay(10);
      digitalWrite(PUMPPIN, HIGH);
      cooler_state = false;
    }
  }
  else {
    if (temp > max_temperature) {
      digitalWrite(PUMPPIN, LOW);
      delay(10);
      digitalWrite(MOTORPIN, LOW);
      cooler_state = true;
    }
  }
}


void read_temperature() {
  // update array
  temp_array[temp_index] = analogRead(ANALOGPIN) / 1024. * 100;
  temp_index += 1;
  temp_index %= TEMPMASIZE;
  // compute temperature average
  temp = 0;
  for(int i = 0; i < TEMPMASIZE; i++) {
    temp += temp_array[i];
  }
  temp /= TEMPMASIZE;
}

void check_mode() {
  mode = "auto";
  int max_button = digitalRead(MAXMODEPIN);
  int min_button = digitalRead(MINMODEPIN);
  if (!max_button) {
    mode = "max";
  }
  if (!min_button) {
    mode = "min";
  }
}

float check_temp_buttons() {
  int increase_button = digitalRead(INCREASETEMPPIN);
  int decrease_button = digitalRead(DECREASETEMPPIN);
  if (!increase_button) {
    return TEMPSTEP;
  }
  if (!decrease_button) {
    return -TEMPSTEP;
  }
  return 0;
}

void update_manifests() {
  manifest_line1 = "temp:" + String(temp, 3);
  if (cooler_state)  {
    manifest_line1 += "   ON";
  }
  else {
    manifest_line1 += "  OFF";
  }
  manifest_line2 = "min" + String(min_temperature, 1) + "  max" + String(max_temperature, 1);
}

void read_thresholds() {
  EEPROM.get(MINTEMPADDR, min_temperature);
  EEPROM.get(MAXTEMPADDR, max_temperature);
}

void write_thresholds() {
  EEPROM.put(MINTEMPADDR, min_temperature);
  EEPROM.put(MAXTEMPADDR, max_temperature);
}

void write_manifests() {
  Serial.println(manifest_line1);
  Serial.println(manifest_line2);
  Serial.println(millis());
  Serial.println("----------");
  lcd.setCursor(0, 0);
  lcd.print(manifest_line1);
  lcd.setCursor(0, 1);
  lcd.print(manifest_line2);
}

void set_thresholds() {
  long int entrance_time = millis();
  long int last_push_time = entrance_time;
  float temp_button = 0;
  String last_mode = mode;
  Serial.println("@set threshold");
  lcd.clear();
  while(millis() - entrance_time < IDLEMILLIS) {
    // update manifest
    manifest_line1 = " max: " + String(max_temperature, 1) + " C";
    manifest_line2 = " min: " + String(min_temperature, 1) + " C";
    if (last_mode == "max") {
      manifest_line1[0] = '*';
    }
    if (last_mode == "min") {
      manifest_line2[0] = '*';
    }
    write_manifests();
    // check if mode is altered
    Serial.println(last_mode);
    check_mode();
    if (mode != "auto") {
      entrance_time = millis();
      last_mode = mode;
      Serial.println("update mode");
      Serial.println(last_mode);
    }
    // check if temperature altered
    temp_button = check_temp_buttons();
    if (temp_button != 0) {
      entrance_time = millis();
      Serial.println("update temp");
      Serial.println(temp_button);
    }
    if (temp_button == 0) {
      continue;
    }
    // update temperature considering debounce
    if (millis() - last_push_time < DEBOUNCEMILLIS) {
      Serial.println("DeBoUnCe...");
      continue;
    }
    last_push_time = millis();
    if (last_mode == "max") {
      max_temperature += temp_button;
    }
    if (last_mode == "min") {
      min_temperature += temp_button;
    }
  }
  write_thresholds();
  lcd.clear();
  mode = "auto";
}
