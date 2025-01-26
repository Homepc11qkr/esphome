ESPHOME RS485 컴포넌트
# ESPHome [![Discord Chat](https://img.shields.io/discord/429907082951524364.svg)](https://discord.gg/KhAMKrd) [![GitHub release](https://img.shields.io/github/release/esphome/esphome.svg)](https://GitHub.com/esphome/esphome/releases/)

[![ESPHome Logo](https://esphome.io/_images/logo-text.png)](https://esphome.io/)

**Documentation:** https://esphome.io/

# 월패드 연동 ESPHOME RS485 컴포넌트

### 2022-04-07 업데이트
1. DEPRECATED API 대응 업데이트


### 2020-04-01 업데이트
1. 체크섬 2byte 대응 checksum2 옵션 추가 (add sum)
2. state_response, sub_device, state_on, state_off, state_** 옵션에 비트(and) 연산 추가
3. 패킷 전송시 ack 설정 없더라도 tx_wait 시간 대기 후 다음 패킷 전송하도록 수정 (일부 월패드 다운 현상 개선)
4. 수동제어 모듈(MAX485 chipset)을 위한 ctrl_pin 옵션 추가

## 하드웨어 구성
따분님 글 참고
https://cafe.naver.com/stsmarthome/10095

## ESPHome 설치
1. 공식사이트 참고하여 설치
https://esphome.io/guides/getting_started_hassio.html
2. external_components 설정으로 RS485 컴포넌트 사용
``` yaml
external_components:
  - source: github://greays/esphome@master
    components: [ rs485 ]
```

## YAML 설정
- 현대통신(imazu) 기준 설정
  - 현대통신은 상태요청 명령이 0.5초 간격으로 자동으로 전송되므로 별도로 상태요청 할 필요 없음

``` yaml
substitutions:
  node_name: rs485
  device_name: "RS485 Controller"

esphome:
  name: ${node_name}
  platform: esp8266
  board: d1_mini

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  manual_ip:
    static_ip: 192.168.0.100
    gateway: 192.168.0.1
    subnet: 255.255.255.0
  reboot_timeout: 20min

external_components:
  - source: github://greays/esphome@master
    components: [ rs485 ]

# RS485 Component (for ttl to rs485 module)
#  - esp8266: UART0 (TX: GPIO1, RX: GPIO3)
#  - esp32: UART2 (TX: GPIO17, RX: GPIO16)
rs485:
  baud_rate: 9600 #Required
  data_bits: 8    #Option(default: 8)
  parity: 0       #Option(default: 0)
  stop_bits: 1    #Option(default: 1)
  
  rx_wait: 10     #Option(default: 10ms) -> 수신 메시지 대기시간 (10ms 미만으로 수신된 메시지만 한 패킷으로 판단)
 tx_interval: 50 #Option(default: 50ms) -> 발신 메시지 전송 간격 (패킷 수신 후 50ms 대기 후 전송)
  tx_wait: 100    #Option(default: 50ms) -> 발신 메시지 Ack 대기시간
  tx_retry_cnt: 3 #Option(default: 3)    -> 발신 메시지 Ack 없을 경우 재시도 횟수
  ctrl_pin: GPIO2 #Option -> 수동 제어 모듈 사용시 셋팅 (MAX485모듈의 DE,RE에 연결된 PIN)
  prefix: [0xF7]  #Option -> 값 세팅시 모든 수신 패킷 Check, 발신 패킷에 Append
  suffix: [0xEE]  #Option -> 값 세팅시 모든 수신 패킷 Check, 발신 패킷에 Append

  checksum: True      #Option(default: False) -> 체크섬 사용여부 (lambda 사용시 세팅 불필요)
  # checksum: |- #Option -> Default(CheckSum8 Xor) 체크섬 아닐 경우 직접 로직 구현(아래 값은 Default 로직임)
  #   // @param: const uint8_t *data, const unsigned short len
  #   // @return: uint8_t
  #   uint8_t crc = 0xF7; // data 변수에는 prefix 제외되어 있음
  #   for(num_t i=0; i<len; i++)
  #     crc ^= data[i];
  #   return crc;
  
  checksum2: False  #Option(default: False) -> ADD 체크섬 사용여부
  # checksum2: !lambda |- #Option -> Default(CheckSum8 Add) 체크섬 아닐 경우 직접 로직 구현(아래 값은 Default 로직임)
  #   // @param: const uint8_t *data, const unsigned short len, const uint8_t checksum1
  #   // @return: uint8_t
  #   uint8_t crc = 0xF7; // data 변수에는 prefix 제외되어 있음
  #   for(num_t i=0; i<len; i++)
  #     crc += data[i];
  #   crc += checksum1; // 첫번째 체크섬 계산 결과
  #   return crc;

  state_response: #Option -> 값 세팅시 response 패킷 수신 후에 명령 패킷 송신
    data: [0x04] #비트연산 시 위치 값 참고 => 1: 0x01, 2: 0x02, 3: 0x04, 4: 0x08, 5: 0x10, 6: 0x20, 7: 0x40, 8: 0x80
    offset: 3
    and_operator: False #Option(default: False) 수신패킷의 offset 위치와 data[0]를 And 비트연산
    inverted: False #Option(default: False) 결과 값 반전(일치하지 않을 경우 참)
  
  # packet_monitor: #Option -> 패킷 모니터: Array 없으면 전체 출력, 있을 경우 or 조건 (logger level DEBUG 추천)
    # - [0x0c, 0x01, 0x2b]  # offset: 0
    # - data: [0x19, 0x04, 0x40, 0x23]
      # offset: 2



sensor:
  - platform: rs485
    name: Livingroom Power Socket 1
    unit_of_measurement: "W"
    device: [0x12, 0x01, 0x1F, 0x04, 0x40, 0x11, 0x00] #Required
    #sub_device: #Option
    #  offset: 0
    #  data: []
    data:
      offset: 8 # 위치
      length: 2 # 길이
      precision: 0 # 소수점



binary_sensor:
  - platform: rs485
    id: balcony
    name: Balcony Light State
    device: [0x0b, 0x01, 0x19, 0x04, 0x40, 0x23, 0x00]
    state_on:
      offset: 7
      data: [0x01]
    state_off:
      offset: 7
      data: [0x02]
    command_state: [0x0B, 0x01, 0x19, 0x01, 0x40, 0x23, 0x00, 0x00] # 상태요청 패킷 (모든 Device에 사용 가능)
    update_interval: 30s # 상태요청 주기



switch:
  # 안방1 콘센트
  # 켜기
  #  0xf7, 0x0b, 0x01, 0x1f, 0x02, 0x40, 0x21, 0x01, 0x00, 0x80, 0xee
  #  0xf7, 0x0b, 0x01, 0x1f, 0x04, 0x40, 0x21, 0x01, 0x01, 0x87, 0xee (ack)
  # 끄기
  #  0xf7, 0x0b, 0x01, 0x1f, 0x02, 0x40, 0x21, 0x02, 0x00, 0x83, 0xee
  #  0xf7, 0x0b, 0x01, 0x1f, 0x04, 0x40, 0x21, 0x02, 0x02, 0x87, 0xee (ack)
  # 켜기상태-> 0xF7 0x12 0x01 0x1F 0x04 0x40 0x21 0x00 0x01 0x00 0x00 0x00 0x00 0x00 0x00 0x01 0x9E 0xEE
  # 끄기상태-> 0xF7 0x12 0x01 0x1F 0x04 0x40 0x21 0x00 0x02 0x00 0x00 0x00 0x00 0x00 0x00 0x01 0x9D 0xEE
  - platform: rs485
    name: "ROOM1 Power Socket 1"
    icon: "mdi:power-socket-eu"
    device: [0x12, 0x01, 0x1F, 0x04, 0x40, 0x21, 0x00]
    state_on:
      offset: 7
      data: [0x01]
    state_off:
      offset: 7
      data: [0x02]
    command_on:
      data: [0x0b, 0x01, 0x1f, 0x02, 0x40, 0x21, 0x01, 0x00]
      ack: [0x0b, 0x01, 0x1f, 0x04, 0x40, 0x21, 0x01, 0x01]
    command_off:
      data: [0x0b, 0x01, 0x1f, 0x02, 0x40, 0x21, 0x02, 0x00]
      ack: [0x0b, 0x01, 0x1f, 0x04, 0x40, 0x21, 0x02, 0x02]



# RS485 Light(like Binary Light)
light:
  # [안방1]
  # 켜짐 상태-> 0xf7, 0x0b, 0x01, 0x19, 0x04, 0x40, 0x21, 0x00, 0x01, 0x80, 0xee
  # 꺼짐 상태-> 0xf7, 0x0b, 0x01, 0x19, 0x04, 0x40, 0x21, 0x00, 0x02, 0x83, 0xee
  # 켜짐 명령-> 0xf7, 0x0b, 0x01, 0x19, 0x02, 0x40, 0x21, 0x01, 0x00, 0x86, 0xee
  # 꺼짐 명령-> 0xf7, 0x0b, 0x01, 0x19, 0x02, 0x40, 0x21, 0x02, 0x00, 0x85, 0xee
  - platform: rs485
    name: "ROOM1 1"
    device: [0x0b, 0x01, 0x19, 0x04]
    sub_device:
      offset: 5
      data: [0x21]
    state_on:
      offset: 7
      data: [0x01]
      and_operator: true
      inverted: false
    state_off:
      offset: 7
      data: [0x01]
      and_operator: true
      inverted: true
    command_on:
      data: [0x0b, 0x01, 0x19, 0x02, 0x40, 0x21, 0x01, 0x00]
      ack: [0x0b, 0x01, 0x19, 0x04, 0x40, 0x21, 0x01, 0x01]
    command_off:
      data: [0x0b, 0x01, 0x19, 0x02, 0x40, 0x21, 0x02, 0x00]
      ack: [0x0b, 0x01, 0x19, 0x04, 0x40, 0x21, 0x02, 0x02]



# RS485 Fan
fan:
  # [환기]
  # 켜짐(강) 상태-> 0xf7, 0x0c, 0x01, 0x2b, 0x04, 0x40, 0x11, 0x00, 0x01, 0x07, 0x82, 0xee
  # 켜짐(중) 상태-> 0xf7, 0x0c, 0x01, 0x2b, 0x04, 0x40, 0x11, 0x00, 0x01, 0x03, 0x86, 0xee
  # 켜짐(약) 상태-> 0xf7, 0x0c, 0x01, 0x2b, 0x04, 0x40, 0x11, 0x00, 0x01, 0x01, 0x84, 0xee
  # 꺼짐     상태-> 0xf7, 0x0c, 0x01, 0x2b, 0x04, 0x40, 0x11, 0x00, 0x02, 0x00, 0x86, 0xee
  # 켜짐(강) 명령-> 0xf7, 0x0b, 0x01, 0x2b, 0x02, 0x40, 0x11, 0x01, 0x00, 0x84, 0xee
  # 켜짐(중) 명령-> 0xf7, 0x0b, 0x01, 0x2b, 0x02, 0x42, 0x11, 0x03, 0x00, 0x84, 0xee
  # 켜짐(약) 명령-> 0xf7, 0x0b, 0x01, 0x2b, 0x02, 0x42, 0x11, 0x01, 0x00, 0x86, 0xee
  # 꺼짐     명령-> 0xf7, 0x0b, 0x01, 0x2b, 0x02, 0x40, 0x11, 0x02, 0x00, 0x87, 0xee
  - platform: rs485
    name: "Ventilation"
    device: [0x0c, 0x01, 0x2b, 0x04, 0x40, 0x11, 0x00]
    state_on:
      offset: 7
      data: [0x01]
    state_off:
      offset: 7
      data: [0x02]
    command_on:
      data: [0x0b, 0x01, 0x2b, 0x02, 0x40, 0x11, 0x01, 0x00]
      ack: [0x0c, 0x01, 0x2b, 0x04, 0x40, 0x11, 0x01, 0x01, 0x07]
    command_off:
      data: [0x0b, 0x01, 0x2b, 0x02, 0x40, 0x11, 0x02, 0x00]
      ack: [0x0c, 0x01, 0x2b, 0x04, 0x40, 0x11, 0x02, 0x02, 0x00]
    speed: #Option(high, medium, low) -> 없으면 Binary Fan
      high:
        state:
          offset: 7
          data: [0x01, 0x07]
        command:
          data: [0x0b, 0x01, 0x2b, 0x02, 0x40, 0x11, 0x01, 0x00]
          ack: [0x0c, 0x01, 0x2b, 0x04, 0x40, 0x11, 0x01, 0x01, 0x07]
      medium:
        state:
          offset: 7
          data: [0x01, 0x03]
        command:
          data: [0x0b, 0x01, 0x2b, 0x02, 0x42, 0x11, 0x03, 0x00]
          ack: [0x0c, 0x01, 0x2b, 0x04, 0x40, 0x11, 0x01, 0x01, 0x03]
      low:
        state:
          offset: 7
          data: [0x01, 0x01]
        command:
          data: [0x0b, 0x01, 0x2b, 0x02, 0x42, 0x11, 0x01, 0x00]
          ack: [0x0c, 0x01, 0x2b, 0x04, 0x40, 0x11, 0x01, 0x01, 0x01]



# RS485 Climate
climate:
  # [거실 난방] 0x11
  # 상태 요청: 0xF7, 0x0B, 0x01, 0x18, 0x01, 0x45, 0x11, 0x00, 0x00, 0xB0, 0xEE
  # 켜짐 상태: 0xF7, 0x0D, 0x01, 0x18, 0x04, 0x45, 0x11, 0x00, (0x01, 0x1B, 0x17), 0xBE, 0xEE (상태, 현재온도, 설정온도)
  # 꺼짐 상태: 0xF7, 0x0D, 0x01, 0x18, 0x04, 0x45, 0x11, 0x00, (0x04, 0x1B, 0x17), 0xBB, 0xEE (상태, 현재온도, 설정온도)
  # 외출 상태: 0xF7, 0x0D, 0x01, 0x18, 0x04, 0x45, 0x11, 0x00, (0x07, 0x1B, 0x17), 0xB9, 0xEE
  # 켜짐 명령: 0xF7, 0x0B, 0x01, 0x18, 0x02, 0x46, 0x11, 0x01, 0x00, 0xB1, 0xEE
  #      ACK: 0xF7, 0x0D, 0x01, 0x18, 0x04, 0x46, 0x11, 0x01, 0x01, 0x1B, 0x17, 0xBC, 0xEE
  # 꺼짐 명령: 0xF7, 0x0B, 0x01, 0x18, 0x02, 0x46, 0x11, 0x04, 0x00, 0xB4, 0xEE
  #      ACK: 0xF7, 0x0D, 0x01, 0x18, 0x04, 0x46, 0x11, 0x04, 0x04, 0x1B, 0x17, 0xBC, 0xEE
  # 온도 조절: 0xF7, 0x0B, 0x01, 0x18, 0x02, 0x45, 0x11, (0x18), 0x00, 0xA7, 0xEE (온도 24도 설정)
  #      ACK: 0xF7, 0x0D, 0x01, 0x18, 0x04, 0x45, 0x11, (0x18), 0x01, (0x1A, 0x18), 0xA8, 0xEE
  - platform: rs485
    name: "Livingroom Heater"
    visual:
      min_temperature: 5 °C
      max_temperature: 40 °C
      temperature_step: 1 °C
    device: [0x0D, 0x01, 0x18, 0x04, 0x45, 0x11, 0x00]
    state_current: #Required (현재온도 State, RS485 Sensor 설정 참고, sensor:로 대체 가능)
      offset: 8
      length: 1
      precision: 0
    state_target: #Required (설정온도 State)
      offset: 9
      length: 1
      precision: 0
    state_off: #Required (끄기 상태)
      offset: 7
      data: [0x04]
    state_heat: #Option (난방모드, 냉방모드: state_cool, 자동모드: state_auto)
      offset: 7
      data: [0x01]
    state_away: #Option (외출모드)
      offset: 7
      data: [0x07]
    command_off: #Required (끄기 명령)
      data: [0x0B, 0x01, 0x18, 0x02, 0x46, 0x11, 0x04, 0x00]
      ack: [0x0D, 0x01, 0x18, 0x04, 0x46, 0x11, 0x04, 0x04]
    command_heat: #Option (난방모드 켜기)
      data: [0x0B, 0x01, 0x18, 0x02, 0x46, 0x11, 0x01, 0x00]
      ack: [0x0D, 0x01, 0x18, 0x04, 0x46, 0x11, 0x01, 0x01]
    command_away: #Option (외출모드)
      data: [0x0B, 0x01, 0x18, 0x02, 0x46, 0x11, 0x07, 0x00]
      ack: [0x0D, 0x01, 0x18, 0x04, 0x46, 0x11, 0x07, 0x07]
    command_home: #Option (재실모드)
      data: [0x0B, 0x01, 0x18, 0x02, 0x46, 0x11, 0x01, 0x00]
      ack: [0x0D, 0x01, 0x18, 0x04, 0x46, 0x11, 0x01, 0x01]
    command_temperature: !lambda |-  #Required (온도 조절)
      // @param: const float x
      return {
                {0x0B, 0x01, 0x18, 0x02, 0x45, 0x11, (uint8_t)x, 0x00},
                {0x0D, 0x01, 0x18, 0x04, 0x45, 0x11, (uint8_t)x, 0x01}
             };



switch:
  # Automation 사용 예졔 (rs485.write) - with ACK
  - platform: template
    name: Automation TEST
    turn_on_action:
      - rs485.write:
          data: [0x0b, 0x01, 0x19, 0x02, 0x40, 0x23, 0x01, 0x00]
          ack: [0x0b, 0x01, 0x19, 0x04, 0x40, 0x23, 0x01, 0x01]
    turn_off_action:
      - rs485.write: !lambda return {{0x0b, 0x01, 0x19, 0x02, 0x40, 0x23, 0x02, 0x00}, {0x0b, 0x01, 0x19, 0x04, 0x40, 0x23, 0x02, 0x02}};
    lambda: |-
      if (id(balcony).state) {
        return true;
      } else {
        return false;
      }

```
