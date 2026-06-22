import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PresentationSession, SessionAnnotation, SessionFlag

@csrf_exempt
@login_required
def start_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        lesson_slug = data.get('lesson_slug')

        session = PresentationSession.objects.create(
            teacher=request.user,
            lesson_slug=lesson_slug
        )

        response_payload = {
            'status': 'success',
            'session_id': str(session_id),
            'lesson_slug': session.lesson_slug
        }

        return JsonResponse(response_payload)

    response_payload = {
        'status': 'error',
        'message': 'Invalid request'
    }

    return JsonResponse(response_payload, status=400)

@csrf_exempt
@login_required
def save_annotation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session = PresentationSession.objects.filter(
            id=data.get('session_id')
            teacher=request.user
        ).first()

        if not session:
            return JsonResponse({'status': 'error', 'message': 'Session not found.'}, status=404)

        SessionAnnotation.objects.create(
            session=session,
            slide_index=data.get('slide_index'),
            content_data=data.get('content_data')
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required
def flag_slide(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session = PresentationSession.objects.filter(
            id=data.get('session_id'),
            teacher=request.user
        ).first()

        if not session:
            return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)

        SessionFlag.objects.create(
            session=session,
            slide_index=data.get('slide_index'),
            flag_type=data.get('flag_type'),
            notes=data.get('notes', '')
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
