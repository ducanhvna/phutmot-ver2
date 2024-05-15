from django.test import TestCase

# Create your tests here.
from apps.vantaihahai.utils.core import VanTaiHaHai
def test_001():
    vantai = VanTaiHaHai()

    hanhtrinh = 15608
    url = 'https://i.imgur.com/lmMVQ9l.jpeg'
    km_end = 1000000
    attackements = [url]
    vantai.capnhatsokmketthuchanhtrinh(hanhtrinh, km_end, None, attackements)