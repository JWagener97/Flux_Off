#define NUM_SAMPLES 10  // number of samples to average
#define PERIOD 250        // Period in microseconds (4000Hz)

int index = 0; // index to keep track of current position in array
const int adcPin = A0;   // Analog pin to read from
unsigned long last_us = 0L;  // Last time sample was taken
bool start = false; // Flag used to start the sampling
int samples[NUM_SAMPLES];    // array to store samples
int sum = 0;

void setup()
{
  Serial.begin(115200);
}

void loop()
{
  // Check for incoming serial commands

  if (start == false)
  {
    sample();
    if (Serial.available() > 0) 
    {
      String command = Serial.readStringUntil('\n');
      command.trim(); // Remove leading/trailing whitespaces
      // Check if the received command is "Sample"
      if (command == "Sample") 
      {
        start = true;
      }
    }
  } 
  else 
  {
    if (micros() - last_us > PERIOD)
    {
      last_us += PERIOD;
      sample();
    }
  }


}

void sample()
{
  int new_value = analogRead(adcPin); // Read new sample
  sum = sum - samples[index] + new_value;
  samples[index] = new_value;
  float moving_average = (float)sum / NUM_SAMPLES;
  if (start == true)
  {
  Serial.println(moving_average);
  }
  index = (index + 1) % NUM_SAMPLES;
}
