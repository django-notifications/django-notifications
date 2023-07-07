# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
import datetime

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils import timesince, timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from notifications.querysets import NotificationQuerySet


class NotificationLevel(models.IntegerChoices):
    SUCCESS = 1
    INFO = 2
    WARNING = 3
    ERROR = 4


class AbstractNotification(models.Model):
    """
    Action model describing the actor acting out a verb (on an optional
    target).
    Nomenclature based on http://activitystrea.ms/specs/atom/1.0/

    Generalized Format::

        <actor> <verb> <time>
        <actor> <verb> <target> <time>
        <actor> <verb> <action_object> <target> <time>

    Examples::

        <justquick> <reached level 60> <1 minute ago>
        <brosner> <commented on> <pinax/pinax> <2 hours ago>
        <washingtontimes> <started follow> <justquick> <8 minutes ago>
        <mitsuhiko> <closed> <issue 70> on <mitsuhiko/flask> <about 2 hours ago>

    Unicode Representation::

        justquick reached level 60 1 minute ago
        mitsuhiko closed issue 70 on mitsuhiko/flask 3 hours ago

    HTML Representation::

    <a href="http://test.com/">brosner</a> commented on <a href="http://gh.com/pinax/pinax">pinax/pinax</a> 2 hours ago

    """

    level = models.IntegerField(_("level"), choices=NotificationLevel.choices, default=NotificationLevel.INFO)

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("recipient"),
        blank=False,
    )
    unread = models.BooleanField(_("unread"), default=True, blank=False, db_index=True)

    actor_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="notify_actor", verbose_name=_("actor content type")
    )
    actor_object_id = models.CharField(_("actor object id"), max_length=255)
    actor = GenericForeignKey("actor_content_type", "actor_object_id")
    actor.short_description = _("actor")

    verb = models.CharField(_("verb"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)

    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="notify_target",
        verbose_name=_("target content type"),
        blank=True,
        null=True,
    )
    target_object_id = models.CharField(_("target object id"), max_length=255, blank=True, null=True)
    target = GenericForeignKey("target_content_type", "target_object_id")
    target.short_description = _("target")

    action_object_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="notify_action_object",
        verbose_name=_("action object content type"),
        blank=True,
        null=True,
    )
    action_object_object_id = models.CharField(_("action object object id"), max_length=255, blank=True, null=True)
    action_object = GenericForeignKey("action_object_content_type", "action_object_object_id")
    action_object.short_description = _("action object")

    timestamp = models.DateTimeField(_("timestamp"), default=timezone.now, db_index=True)

    public = models.BooleanField(_("public"), default=True, db_index=True)
    deleted = models.BooleanField(_("deleted"), default=False, db_index=True)
    emailed = models.BooleanField(_("emailed"), default=False, db_index=True)

    data = models.JSONField(_("data"), blank=True, null=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ("-timestamp",)
        # speed up notifications count query
        index_together = ("recipient", "unread")
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        ctx = {
            "actor": self.actor,
            "verb": self.verb,
            "action_object": self.action_object,
            "target": self.target,
            "timesince": self.timesince(),
        }
        if self.target:
            if self.action_object:
                return _("%(actor)s %(verb)s %(action_object)s on %(target)s %(timesince)s ago") % ctx
            return _("%(actor)s %(verb)s %(target)s %(timesince)s ago") % ctx
        if self.action_object:
            return _("%(actor)s %(verb)s %(action_object)s %(timesince)s ago") % ctx
        return _("%(actor)s %(verb)s %(timesince)s ago") % ctx

    def timesince(self, now: None | datetime.datetime = None) -> str:
        """
        Shortcut for the ``django.utils.timesince.timesince`` function of the
        current timestamp.
        """

        return timesince.timesince(self.timestamp, now)

    @property
    def slug(self):
        return self.id

    def mark_as_read(self) -> None:
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self) -> None:
        if not self.unread:
            self.unread = True
            self.save()

    def actor_object_url(self) -> str:
        try:
            url = reverse(
                f"admin:{self.actor_content_type.app_label}_{self.actor_content_type.model}_change",
                args=(self.actor_object_id,),
            )
            return format_html("<a href='{url}'>{id}</a>", url=url, id=self.actor_object_id)
        except NoReverseMatch:
            return self.actor_object_id

    def action_object_url(self) -> str:
        try:
            url = reverse(
                f"admin:{self.action_object_content_type.app_label}_{self.action_object_content_type.model}_change",
                args=(self.action_object_id,),
            )
            return format_html("<a href='{url}'>{id}</a>", url=url, id=self.action_object_object_id)
        except NoReverseMatch:
            return self.action_object_object_id

    def target_object_url(self) -> str:
        try:
            url = reverse(
                f"admin:{self.target_content_type.app_label}_{self.target_content_type.model}_change",
                args=(self.target_object_id,),
            )
            return format_html("<a href='{url}'>{id}</a>", url=url, id=self.target_object_id)
        except NoReverseMatch:
            return self.target_object_id

    def naturalday(self):
        """
        Shortcut for the ``humanize``.
        Take a parameter humanize_type. This parameter control the which humanize method use.
        Return ``today``, ``yesterday`` ,``now``, ``2 seconds ago``etc.
        """

        return naturalday(self.timestamp)

    def naturaltime(self):
        return naturaltime(self.timestamp)
