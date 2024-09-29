import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(subject, html, from_addr, to_addr, cc_addr, password, file_path,conteo):
    # Crea una instancia del objeto MIMEMultipart
    msg = MIMEMultipart()

    # Configura los atributos del mensaje
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_addr)
    msg['CC'] = ', '.join(cc_addr)
    msg['Subject'] = subject
    with open(html, 'r') as file:
        html_content = file.read()
        
    html_content = html_content.replace('{{conteo}}', str(conteo))
    # Agrega el mensaje al correo
    msg.attach(MIMEText(html_content, 'html'))

    # Adjunta el archivo
    attachment = open(file_path, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= "+ file_path)
    msg.attach(part)

    # Crea una conexión segura con el servidor SMTP utilizando SSL
    server = smtplib.SMTP('smtp.office365.com', 587)  # Usa el servidor SMTP de Outlook
    server.ehlo()
    server.starttls()
    server.ehlo()
    # Inicia sesión en la cuenta de correo
    server.login(from_addr, password)

    # Envia el correo
    text = msg.as_string()
    server.sendmail(from_addr, to_addr + cc_addr, text)

    # Cierra la conexión con el servidor
    server.quit()


def error_email(subject, html, from_addr, to_addr, cc_addr, password, hora, error):
    # Crea una instancia del objeto MIMEMultipart
    msg = MIMEMultipart()
    with open(html, 'r') as file:
        html_content = file.read()
    # Configura los atributos del mensaje
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_addr)
    msg['CC'] = ', '.join(cc_addr)
    msg['Subject'] = subject

    html_content = html_content.replace('{{hora}}', hora)
    html_content = html_content.replace('{{error}}', error)

    # Agrega el mensaje al correo
    msg.attach(MIMEText(html_content, 'html'))


    # Crea una conexión segura con el servidor SMTP utilizando SSL
    server = smtplib.SMTP('smtp.office365.com', 587)  # Usa el servidor SMTP de Outlook
    server.ehlo()
    server.starttls()
    server.ehlo()
    # Inicia sesión en la cuenta de correo
    server.login(from_addr, password)

    # Envia el correo
    text = msg.as_string()
    server.sendmail(from_addr, to_addr + cc_addr, text)

    # Cierra la conexión con el servidor
    server.quit()

