import factory

from notifications.models.base import NotificationLevel
from notifications.tests.factories import users as user_factory


def test_main_migration0002(migrator):
    """Ensures that the second migration works."""
    old_state = migrator.apply_initial_migration(("notifications", "0011_notification_new_level"))

    OldUser = old_state.apps.get_model("auth", "User")  # pylint: disable=invalid-name
    OldNotification = old_state.apps.get_model("notifications", "Notification")  # pylint: disable=invalid-name
    OldContentType = old_state.apps.get_model("contenttypes", "ContentType")  # pylint: disable=invalid-name

    mark_follower = factory.create(OldUser, FACTORY_CLASS=user_factory.RecipientFactory)
    guido = factory.create(OldUser, FACTORY_CLASS=user_factory.TargetFactory)
    mark = factory.create(OldUser, FACTORY_CLASS=user_factory.ActorFactory)

    user_type = OldContentType.objects.get_for_model(mark)
    notification_base = {
        "recipient": mark_follower,
        "actor_content_type": user_type,
        "actor_object_id": mark.pk,
        "verb": "start follow",
        "target_content_type": user_type,
        "target_object_id": guido.pk,
    }
    OldNotification(level="success", **notification_base).save()
    OldNotification(level="info", **notification_base).save()
    OldNotification(level="warning", **notification_base).save()
    OldNotification(level="error", **notification_base).save()

    assert OldNotification.objects.count() == 4
    assert OldNotification.objects.filter(level="info").count() == 1
    assert OldNotification.objects.filter(new_level=NotificationLevel.INFO).count() == 4

    new_state = migrator.apply_tested_migration(("notifications", "0012_auto_20230601_1905"))
    NewNotification = new_state.apps.get_model("notifications", "Notification")  # pylint: disable=invalid-name

    assert NewNotification.objects.count() == 4
    assert NewNotification.objects.filter(new_level=NotificationLevel.SUCCESS).count() == 1
    assert NewNotification.objects.filter(new_level=NotificationLevel.INFO).count() == 1
    assert NewNotification.objects.filter(new_level=NotificationLevel.WARNING).count() == 1
    assert NewNotification.objects.filter(new_level=NotificationLevel.ERROR).count() == 1

    new_state_2 = migrator.apply_tested_migration(("notifications", "0014_rename_new_level_notification_level"))
    NewNotification2 = new_state_2.apps.get_model("notifications", "Notification")  # pylint: disable=invalid-name

    assert NewNotification2.objects.count() == 4
    assert NewNotification2.objects.filter(level=NotificationLevel.SUCCESS).count() == 1
    assert NewNotification2.objects.filter(level=NotificationLevel.INFO).count() == 1
    assert NewNotification2.objects.filter(level=NotificationLevel.WARNING).count() == 1
    assert NewNotification2.objects.filter(level=NotificationLevel.ERROR).count() == 1
