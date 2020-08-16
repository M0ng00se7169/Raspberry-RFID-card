# RFID Raspberry Card Manager [![Status](https://img.shields.io/badge/status-finished-brightgreen)](https://github.com/Ukasz09/RFID-card-reading)

RFID Raspberry Pi Card Manager written in Python with MVC and MQTT patterns
<br/>
- :white_check_mark: Client server publish/subscribe messaging pattern (by using MQTT 3.1.1 protocol) <br/>
- :white_check_mark: Security and authentication (By using SSL and uthentication mechanism)
- :white_check_mark: MVC (Model-View-Controller)


## How to use it
1. Install required packages (MQTT) <br/>

```bash
pip install -r requirements.txt --user
```
2. Generate certificates and keys: <br/>
   Generate pair of keys: <br/>
	`openssl genrsa -des3 -out ca.key 2048` <br/>
   Make certificate: <br/>
	`openssl req -new -x509 -days 1826 -key ca.key -out ca.crt` <br/>
   Make another pair of keys: <br/>
	`openssl genrsa -out server.key 2048` <br/>
	Sign certificate: <br/>
	`openssl req -new -out server.csr -key server.key` <br/>
	Verify certificate <br/>
	`openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 360` <br/>

3.	Make password file (in your mosquitto installation folder, e.g. `/etc/mosquitto/`): <br/>
	`mosquitto_passwd -c passwd.conf server` 
4.  Modify mosquitto.conf file. Append this lines to it: 
	```bash
	allow_anonymous false
	password_file //path to passwd.conf which you had made in section 3//
	port 8883
	cafile //path to ca.crt which you had made in section 2//
	certfile //path to server.crt which you had made in section 2//
	keyfile //path to server.key which you had made in section 2//
	```
5. Navigate to client and server directory
6. Run script:
```bash
python3 main.py
```

___
## 📫 Contact 
Feel free to contact me! ✊
