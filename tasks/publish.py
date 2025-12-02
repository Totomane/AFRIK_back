from celery import shared_task
from oauth.models import Publication, SocialToken
from services.youtube_services import YouTubeService
from services.linkedin_service import LinkedInService
from services.x_service import XService

@shared_task(bind=True)
def publish_media(self, pub_id):
    pub = Publication.objects.get(id=pub_id)
    token = SocialToken.objects.get(user=pub.user, provider=pub.provider)

    pub.status = 'uploading'
    pub.save(update_fields=['status'])

    try:
        if pub.provider == 'youtube':
            svc = YouTubeService(token.__dict__)
        elif pub.provider == 'linkedin':
            svc = LinkedInService(access_token=token.access_token, user_id=str(token.user.id))
        elif pub.provider == 'x':
            svc = XService(token.access_token)
        else:
            return

        post_id = svc.upload_and_post(pub)
        pub.provider_post_id = post_id
        pub.status = 'live'
        pub.save()
    except Exception as e:
        pub.status = 'failed'
        pub.error = str(e)
        pub.save()
        raise self.retry(exc=e)
