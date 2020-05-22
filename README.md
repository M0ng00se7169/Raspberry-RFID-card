# RFID Raspberry Card Manager [![Status](https://img.shields.io/badge/status-finished-brightgreen)](https://github.com/M0ng00se7169/Raspberry-RFID-card)

<hr/>

RFID Raspberry Pi Card Manager written in Python with MVC and MQTT patterns

- ✅ Client server publish/subscribe messaging pattern (by using MQTT 3.1.1 protocol)
- ✅ Security and authentication (By using SSL and authentication mechanism)
- ✅ MVC (Model-View-Controller)

## How to use it
<hr/>
1: Install required packages (MQTT)

```bash
    pip install -r requirements.txt --user
```
<hr/>

2: Generate certificates and keys:
- Generate a pair of keys:
```bash
    openssl genrsa -des3 -out ca.key 2048
```
- Make certificate:
```bash
    openssl req -new -x509 -days 1826 -key ca.key -out ca.crt
```
- Make another pair of keys:
```bash
    openssl genrsa -out server.key 2048
```
- Sign certificate:
```bash
    openssl req -new -out server.csr -key server.key
```
- Verify certificate:
```bash
    openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 360
```
<hr/>
3: Make password file (in your mosquitto installation folder, e.g. <code>/etc/mosquitto/</code>):

```bash
    mosquitto_passwd -c passwd.conf server
```
<hr/>
4: Modify mosquitto.conf file. Append this lines to it:

```code
    allow_anonymous false
    password_file           //path to passwd.conf which you had made in section 3//
    port 8883
    cafile                  //path to ca.crt which you had made in section 2//
    certfile                //path to server.crt which you had made in section 2//
    keyfile                 //path to server.key which you had made in section 2//
```
<hr/>
5: Navigate to client and server directory

6: Run script:
```bash
    python3 main.py
```

## 📫 Contact 
Feel free to contact me! ✊