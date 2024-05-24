bool start = false; // Flag used to start the sampling
const int bufferSize = 10; // Adjust this value to change the length of the moving average
int readings[bufferSize]; // Array to store the most recent readings
int readIndex = 0; // Index of the current reading
int total = 0; // Total of the readings in the buffer
int average = 0; // Moving average of the readings

void setup() 
{
  Serial.begin(115200);
  // Initialize the readings array to zero
  for (int i = 0; i < bufferSize; i++) 
  {
    readings[i] = 0;
  }
  
  while (!start) 
  {
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
}

void loop() 
{
  if (start) 
  {
    static uint32_t last_conversion_time = micros();
    if (micros() - last_conversion_time >= 50) 
    {
      last_conversion_time += 50;

      // Subtract the last reading from the total
      total = total - readings[readIndex];
      
      // Read the current analog value
      readings[readIndex] = analogRead(A0);
      
      // Add the current reading to the total
      total = total + readings[readIndex];
      
      // Advance to the next position in the array
      readIndex = (readIndex + 1) % bufferSize;

      // Calculate the average
      average = total / bufferSize;
      if (readIndex == 9)
      {
      // Send the average value
      Serial.print(last_conversion_time);
      Serial.print(",");
      Serial.println(average);
      }
    }
  }
}
