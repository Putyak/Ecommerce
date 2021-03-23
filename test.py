# from bs4 import BeautifulSoup
# import uuid
# import requests
#
# orderId = "https://sandbox3.payture.com/apim/Init?Key=Merchant&Data=SessionType%3DPay%3BOrderId%3D" + str(uuid.uuid4()) + "%3BProduct%3DTicket%3BTotal%3D125.76%3BAmount%3D12576"
#
# xml_string = requests.get(orderId)
# soup = BeautifulSoup(str(xml_string.text), 'xml')
# tag = soup.Init
# print("https://sandbox3.payture.com/apim/Pay?SessionId=" + tag['SessionId'])


# import itertools
# import operator
# INPUT=[
#   {'group_id' : 1, 'name' : 'aaa', 'age' : 111},
#   {'group_id' : 1, 'name' : 'bbb', 'age' : 222},
#   {'group_id' : 2, 'name' : 'ccc', 'age' : 333},
#   {'group_id' : 2, 'name' : 'ddd', 'age' : 444},
#   {'group_id' : 3, 'name' : 'eee', 'age' : 555},
#   {'group_id' : 3, 'name' : 'fff', 'age' : 666},
# ]
#
#
# def groupid_drop(d):
#     del d['group_id']
#     return d
#
#
# RESULT=[{'group_id': i, 'data': list(map(groupid_drop, grp))} for i, grp in itertools.groupby(INPUT, operator.itemgetter('group_id'))]
# print(RESULT)

#
# INPUT=[
#   {
#     "count": 1,
#     "good_id": "1",
#     "price": 346,
#     "purchase_id": "3be3c442-dbd4-4afc-8407-37ddc4fee883"
#   },
#   {
#     "count": 1,
#     "good_id": "2",
#     "price": 700,
#     "purchase_id": "3be3c442-dbd4-4afc-8407-37ddc4fee883"
#   },
#   {
#     "count": 1,
#     "good_id": "1",
#     "price": 346,
#     "purchase_id": "50162066-e0a4-49e2-a792-9c4622cbdfb7"
#   },
#   {
#     "count": 1,
#     "good_id": "2",
#     "price": 700,
#     "purchase_id": "50162066-e0a4-49e2-a792-9c4622cbdfb7"
#   },
#   {
#     "count": 1,
#     "good_id": "3",
#     "price": 723,
#     "purchase_id": "50162066-e0a4-49e2-a792-9c4622cbdfb7"
#   }
# ]
# def groupid_drop(d):
#     del d['purchase_id']
#     return d
# RESULT=[{'purchase_id': i, 'data': map(groupid_drop, grp)} for i, grp in itertools.groupby(INPUT, operator.itemgetter('purchase_id'))]
#
# print(RESULT)
