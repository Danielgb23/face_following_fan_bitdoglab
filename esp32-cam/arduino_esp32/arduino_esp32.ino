//esp32 by Espressif Systems version 3.2.0

#include "esp_camera.h"
#include <WiFi.h>
#include <WiFiUdp.h>


// WiFi config
const char* ssid = "DLEA801";
const char* password = "fanrobot";

// mock DNS UDP config
const int picPort = 12346;
const char* backend_name="backend";

//timer interrupt
esp_timer_handle_t timer;
volatile bool requestFlag = true;

WiFiUDP udp;
WiFiUDP udp_dns;
String udpAddress;

//mock dns server resolve function
String resolve_name(const char* name) {
  String message = "RESOLVE " + String(name);

  udp_dns.beginPacket("255.255.255.255", 12347);
  udp_dns.print(message);
  udp_dns.endPacket();

  delay(20);  // Wait for server to respond

  int packetSize = udp_dns.parsePacket();
  if (packetSize) {
    char reply[64];
    int len = udp_dns.read(reply, sizeof(reply) - 1);
    reply[len] = '\0';
    return String(reply);
  } else {
    return "\0";
  }
}

void startCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.pin_xclk = 0;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if(psramFound()){
    config.frame_size = FRAMESIZE_QVGA; //320 × 240
    config.jpeg_quality = 3;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QQVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  sensor_t * s = esp_camera_sensor_get();
  s->set_brightness(s, 1);     // -2 to 2
  s->set_contrast(s, -1);       // -2 to 2
  s->set_saturation(s, 0);     // -2 to 2
  s->set_gain_ctrl(s, 1);      // Auto gain
  s->set_exposure_ctrl(s, 1);  // Auto exposure
  s->set_awb_gain(s, 1);       // Auto white balance gain

  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

//timer interrupt
void  onTimer(void * arg) {
  requestFlag = true;  // Set flag on interrupt
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");

  startCamera();
  udp.begin(picPort);
  udp_dns.begin(12347);

   // Create a periodic timer
  const esp_timer_create_args_t timer_args = {
      .callback = &onTimer,
      .arg = nullptr,
      .dispatch_method = ESP_TIMER_TASK,
      .name = "periodic_timer"
  };

  
  esp_timer_create(&timer_args, &timer);
  esp_timer_start_periodic(timer, 10 * 1000000);  // 10s in microseconds
}

void loop() {
  if (requestFlag) {
    requestFlag = false;
    udpAddress="\0";
    //request backend address
    while(udpAddress[0]=='\0'){
      udpAddress = resolve_name(backend_name);
    }
  }

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }

  // Send image size first
  udp.beginPacket(udpAddress.c_str(), picPort);
  udp.write((uint8_t*)&fb->len, sizeof(fb->len));
  udp.endPacket();

  // Send image data in chunks (max 1460 bytes per UDP packet)
  const size_t maxPacketSize = 1460;
  size_t sent = 0;
  while (sent < fb->len) {
    size_t packetSize = min(maxPacketSize, fb->len - sent);
    udp.beginPacket(udpAddress.c_str(), picPort);
    udp.write(fb->buf + sent, packetSize);
    udp.endPacket();
    sent += packetSize;
    delay(1);
  }

  esp_camera_fb_return(fb);
  delay(100);  // capture every []ms
}