"""
BİDB'nin personel bilgisi sorgulama API'sine bağlanır.
"""

#import requests
#
#STAFF_LOOKUP_URL = "https://api.mu.edu.tr/v1/staff/info"
#STAFF_LOOKUP_SERVICE_TOKEN = "BURAYA_GERCEK_TOKEN_GELECEK"
#
#
#def lookup_staff_by_email(email: str) -> dict | None:
#    try:
#        response = requests.post(
#            STAFF_LOOKUP_URL,
#            json={
#                "ServiceToken": STAFF_LOOKUP_SERVICE_TOKEN,
#                "Email": email,
#            },
#            timeout=5,
#        )
#        result = response.json()
#    except Exception:
#        return None
#
#    if not result.get("success"):
#        return None
#
#    data = result.get("data")
#    if not data:
#        return None
#
#    return {
#        "name": data.get("name") or data.get("Name"),
#        "surname": data.get("surname") or data.get("Surname"),
#        "title": data.get("title") or data.get("Title"),
#        "title_english": data.get("titleEnglish") or data.get("TitleEnglish"),
#        "type": data.get("type") or data.get("Type"),
#
#        "working_unit_name": data.get("workingUnit") or data.get("WorkingUnit"),
#
#        "picture_source": data.get("pictureSource") or data.get("PictureSource"),
#        "email": data.get("email") or data.get("Email"),
#        "office_phone": data.get("officePhone") or data.get("OfficePhone"),
#        "gsm": data.get("gsm") or data.get("Gsm"),
#        "status": data.get("status") or data.get("Status"),
#    }
#
#
_FAKE_STAFF_DATABASE = [
    {
        "name": "ARDA",
        "surname": "ŞİMŞEK",
        "title": "Öğretim Görevlisi",
        "titleEnglish": "Lecturer",
        "workingUnit": "DİJİTAL DÖNÜŞÜM VE VERİ YÖNETİMİ KOORDİNATÖRLÜĞÜ",
        "email": "arda@mu.edu.tr",
        "officePhone": "0252 212 1234",
        "status": "1",
    },
]


def _call_fake_api(name: str, surname: str) -> dict:
   
    name_normalized = name.strip().lower()
    surname_normalized = surname.strip().lower()

    for staff in _FAKE_STAFF_DATABASE:
        if (
            staff["name"].strip().lower() == name_normalized
            and staff["surname"].strip().lower() == surname_normalized
        ):
            return {
                "success": True,
                "message": None,
                "data": staff,
            }

    return {
        "success": False,
        "message": "Personel bulunamadı.",
        "data": None,
    }


def _call_fake_api_by_email(email: str) -> dict:

    email_normalized = email.strip().lower()

    for staff in _FAKE_STAFF_DATABASE:
        if staff["email"].strip().lower() == email_normalized:
            return {
                "success": True,
                "message": None,
                "data": staff,
            }

    return {
        "success": False,
        "message": "Bu e-posta için personel bulunamadı.",
        "data": None,
    }


def lookup_staff_by_email(email: str) -> dict | None:

    raw_response = _call_fake_api_by_email(email)

    if not raw_response.get("success"):
        return None

    data = raw_response.get("data")
    if not data:
        return None

    return {
        "name": data.get("name"),
        "surname": data.get("surname"),
        "title": data.get("title"),
        "title_english": data.get("titleEnglish"),
        "working_unit": data.get("workingUnit"),
        "email": data.get("email"),
        "office_phone": data.get("officePhone"),
        "status": data.get("status"),
    }


def lookup_staff_by_name(name: str, surname: str) -> dict | None:
  
    raw_response = _call_fake_api(name, surname)

    if not raw_response.get("success"):
        return None

    data = raw_response.get("data")
    if not data:
        return None

    return {
        "name": data.get("name"),
        "surname": data.get("surname"),
        "title": data.get("title"),
        "title_english": data.get("titleEnglish"),
        "working_unit": data.get("workingUnit"),
        "email": data.get("email"),
        "office_phone": data.get("officePhone"),
        "status": data.get("status"),
    }