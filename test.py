from bs4 import BeautifulSoup
import uuid
import requests

orderId = "https://sandbox3.payture.com/apim/Init?Key=Merchant&Data=SessionType%3DPay%3BOrderId%3D" + str(uuid.uuid4()) + "%3BProduct%3DTicket%3BTotal%3D125.76%3BAmount%3D12576"

xml_string = requests.get(orderId)
soup = BeautifulSoup(str(xml_string.text), 'xml')
tag = soup.Init
print("https://sandbox3.payture.com/apim/Pay?SessionId=" + tag['SessionId'])