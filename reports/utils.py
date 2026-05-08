import os
import json
import base64
import secrets
import random
from pathlib import Path
from dotenv import load_dotenv
from django.conf import settings

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .models import Category, Department

dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)
if OPENAI_API_KEY:
    OPENAI_API_KEY = OPENAI_API_KEY.strip().strip('"').strip("'")
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY) if OpenAI and OPENAI_API_KEY else None

ALLOWED_CATEGORIES = [
    'road_damage',
    'trash_overflow',
    'street_light',
    'graffiti',
    'sidewalk_issue',
    'traffic_sign',
    'other',
]

ALLOWED_PRIORITIES = ['low', 'medium', 'high']

CATEGORY_SYNONYMS = {
    'road_damage': ['road_damage', 'road damage', 'yolun zədələnməsi', 'yol zədələnməsi', 'pothole', 'road damage', 'yol qəzalı'],
    'trash_overflow': ['trash_overflow', 'trash overflow', 'zibil', 'zibillik', 'garbage', 'bin overflow', 'trash', 'zibil axını'],
    'street_light': ['street_light', 'street light', 'street light issue', 'işıqlandırma', 'işıq problemi', 'lamp', 'streetlight'],
    'graffiti': ['graffiti', 'vandalism', 'vandal', 'qraffiti', 'graffiti vandalism', 'grafiti'],
    'sidewalk_issue': ['sidewalk_issue', 'sidewalk issue', 'səki', 'səki problemi', 'footpath', 'pavement'],
    'traffic_sign': ['traffic_sign', 'traffic sign', 'traffic sign issue', 'nişan', 'təhlükəsizlik nişanı', 'traffic sign damaged', 'sign'],
    'other': ['other', 'digər', 'other issue', 'misc', 'unknown', 'unclear']
}


def normalize_category(category_value):
    if not isinstance(category_value, str):
        return 'other'
    value = category_value.strip().lower().replace('-', ' ').replace('_', ' ')
    for slug, synonyms in CATEGORY_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in value:
                return slug
    # Try exact slug match if user returned slug directly
    if value in ALLOWED_CATEGORIES:
        return value
    return 'other'


def generate_dept_token():
    """Generate a secure department token"""
    return secrets.token_urlsafe(32)


def generate_citizen_token():
    """Generate a secure citizen token"""
    return secrets.token_urlsafe(32)


def mock_classify_image(image_path=None):
    """
    Mock AI classification function.
    Returns a fixed JSON response simulating AI image classification.
    """
    categories = [
        {"category": "road_damage", "priority": "high", "description": "Pothole or road surface damage detected"},
        {"category": "trash_overflow", "priority": "medium", "description": "Garbage bin overflowing with waste"},
        {"category": "street_light", "priority": "medium", "description": "Street light malfunction or damage"},
        {"category": "graffiti", "priority": "low", "description": "Unauthorized graffiti on public property"},
        {"category": "sidewalk_issue", "priority": "medium", "description": "Damaged or uneven sidewalk"},
        {"category": "traffic_sign", "priority": "high", "description": "Damaged or missing traffic sign"},
    ]
    
    selected = random.choice(categories)
    confidence = round(random.uniform(0.75, 0.95), 2)
    
    return {
        "category": selected["category"],
        "confidence": confidence,
        "priority": selected["priority"],
        "description": selected["description"],
        "source": "mock"
    }


def _extract_json_object(text):
    text = text.strip()
    json_start = text.find('{')
    json_end = text.rfind('}')
    if json_start == -1 or json_end == -1 or json_end <= json_start:
        raise ValueError('Could not find JSON object in OpenAI response')
    return text[json_start:json_end + 1]


def _parse_openai_response_text(payload):
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        payload = _extract_json_object(payload)
        return json.loads(payload)


def classify_image_with_openai(image_path=None):
    if OPENAI_CLIENT is None:
        raise RuntimeError('OpenAI client is not configured. Set OPENAI_API_KEY in environment and install openai.')

    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')

    prompt = (
        'Sən şəhər xidmətləri üçün vətəndaş şəkilini təsnif edən köməkçisən. '
        'Şəkli təhlil et və yalnız JSON formatında cavab ver. Nəticə yalnız bir JSON obyekt olmalıdır. '\
        'Format belə olmalıdır:\n'
        '{"category":"...","priority":"...","confidence":0.0,"description":"..."}\n'
        'category yalnız bunlardan biri olmalıdır: road_damage, trash_overflow, street_light, graffiti, sidewalk_issue, traffic_sign, other. '\
        'category sahəsindən başqa heç nə yazma. '\
        'priority yalnız bunlardan biri olmalıdır: low, medium, high. '
        'confidence 0.0 ilə 1.0 arasında olmalıdır. '
        'description qısa və azərbaycanca olmalıdır. '
        'Yalnız JSON obyekt ver, əlavə izah yazma.'
    )

    print('OpenAI image classification: sending request...')
    response = OPENAI_CLIENT.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{image_base64}'
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )

    raw_output = response.choices[0].message.content
    classification_result = _parse_openai_response_text(raw_output)
    category_raw = classification_result.get('category', 'other')
    classification_result['category'] = normalize_category(category_raw)
    classification_result['priority'] = classification_result.get('priority', 'medium')
    classification_result['confidence'] = float(classification_result.get('confidence', 0))
    classification_result['description'] = classification_result.get('description', '').strip()
    classification_result['source'] = 'openai'

    if classification_result['priority'] not in ALLOWED_PRIORITIES:
        classification_result['priority'] = 'medium'
    if not 0 <= classification_result['confidence'] <= 1:
        classification_result['confidence'] = 0.0

    print(f"OpenAI classification result: {classification_result}")
    return classification_result


def real_classify_image(image_path=None):
    """
    Always use real OpenAI AI classification without any fallback.
    """
    if OPENAI_CLIENT is None:
        raise RuntimeError('OpenAI client is not configured. Set OPENAI_API_KEY in environment.')

    print('Using real OpenAI AI classification...')
    return classify_image_with_openai(image_path)


def classify_image(image_path=None):
    if OPENAI_CLIENT is None:
        print('WARNING: OpenAI client is not configured. Please set OPENAI_API_KEY in environment.')
        print('Falling back to mock classification.')
        return mock_classify_image(image_path)

    try:
        print('Using real OpenAI AI classification...')
        return classify_image_with_openai(image_path)
    except Exception as exc:
        print(f'ERROR: OpenAI image classification failed: {exc}')
        print('Falling back to mock classification.')
        return mock_classify_image(image_path)


def _check_smtp_credentials(settings):
    """Return error string if SMTP credentials are missing/placeholder, else None."""
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        return "EMAIL_HOST_USER or EMAIL_HOST_PASSWORD not set."
    placeholders = ('your-', 'ваш', 'app-password', 'change-me')
    if any(p in settings.EMAIL_HOST_PASSWORD.lower() for p in placeholders):
        return "EMAIL_HOST_PASSWORD still contains a placeholder value."
    return None


def _safe_print(text):
    """Print safely on Windows consoles that may not support non-ASCII output."""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(text.encode('ascii', 'replace').decode('ascii'))


def send_email(report):
    """Send HTML email notification to department about new report."""
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from django.conf import settings

    if not report.department or not report.department.email:
        _safe_print(f"WARNING: No department email for report {report.id}")
        return

    err = _check_smtp_credentials(settings)
    if err:
        _safe_print(f"ERROR: {err} Email not sent.")
        return

    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    ai = getattr(report, 'ai_classification', None)
    confidence_display = f"{ai.confidence * 100:.0f}%" if ai else 'N/A'
    subject = "Yeni Sehər Müraciəti - Hərəkət Tələb Olunur"

    ctx = {
        'report': report,
        'ai': ai,
        'site_url': site_url,
        'confidence_display': confidence_display,
    }
    html_body = render_to_string('emails/department_notification.html', ctx)
    # Plain text fallback: safe ASCII summary (email clients that can't render HTML)
    text_body = (
        f"Yeni muraciet: {report.id}\n"
        f"Unvan: {report.address}\n"
        f"Prioritet: {report.priority}\n"
        f"Link: {site_url}/r/{report.dept_token}/"
    ).encode('ascii', 'replace').decode('ascii')

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[report.department.email],
        )
        msg.encoding = 'utf-8'
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
        _safe_print(f"[OK] Department email sent to {report.department.email}")
    except Exception as e:
        _safe_print(f"[ERROR] Failed to send department email: {e}")


def send_citizen_status_email(report, comment=''):
    """Send HTML status-update email to the citizen if they provided an email."""
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.conf import settings

    if not report.citizen_email:
        return

    err = _check_smtp_credentials(settings)
    if err:
        _safe_print(f"ERROR: {err} Citizen email not sent.")
        return

    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    # Subject: ASCII-safe to avoid codec errors on some SMTP relays
    subject = f"Muraciətinizin statusu dəyişdi: {report.status}"

    ctx = {
        'report': report,
        'site_url': site_url,
        'comment': comment,
    }
    html_body = render_to_string('emails/citizen_status_update.html', ctx)
    text_body = (
        f"Status: {report.status}\n"
        f"Link: {site_url}/track/{report.citizen_token}/"
    )

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[report.citizen_email],
        )
        msg.encoding = 'utf-8'
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
        _safe_print(f"[OK] Citizen status email sent to {report.citizen_email}")
    except Exception as e:
        _safe_print(f"[ERROR] Failed to send citizen email: {e}")


def get_or_create_category_from_classification(classification_result, override_category_slug=None):
    """
    Get or create a Category based on AI classification.
    Also assigns a default department if available.
    """
    category_slug = override_category_slug or classification_result["category"]
    category_name = category_slug.replace("_", " ").title()
    
    # Try to get or create the category
    category, created = Category.objects.get_or_create(
        slug=category_slug,
        defaults={
            'name': category_name,
        }
    )
    
    # If category was just created, try to assign a default department
    if created:
        default_dept = Department.objects.filter(is_active=True).first()
        if default_dept:
            category.department = default_dept
            category.save()
    
    return category


def normalize_classification_result(classification_result):
    """
    Normalize the AI classification result.
    If confidence is below 0.6, force the report into an "other" category.
    """
    confidence = float(classification_result.get("confidence", 0))
    if confidence < 0.6:
        classification_result = classification_result.copy()
        classification_result["category"] = "other"
        classification_result["priority"] = "medium"
        classification_result["description"] = classification_result.get(
            "description",
            "AI hesabatı qeyri-müəyyəndir, digər kateqoriya seçilmişdir."
        )
    return classification_result


def get_priority_from_classification(classification_result):
    """
    Get priority from mock AI classification.
    """
    priority = classification_result.get("priority", "medium")
    valid_priorities = ["low", "medium", "high"]
    return priority if priority in valid_priorities else "medium"
