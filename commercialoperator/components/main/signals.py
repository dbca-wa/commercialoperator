from django.db.models import Q
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from commercialoperator.components.main.models import Activity, Park, Trail, Zone

import logging

logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender=Park.allowed_activities.through)
def handle_removed_park_activities(sender, instance, **kwargs):
    post_remove = kwargs.get("action") == "post_remove"
    if not post_remove:
        return
    pk_set = kwargs.get("pk_set", [])
    activities = Activity.objects.filter(id__in=pk_set)

    from commercialoperator.components.proposals.models import (
        Proposal,
        ProposalPark,
        ProposalParkActivity,
        ProposalEventsParks,
    )

    exclude_statuses = [
        Proposal.PROCESSING_STATUS_APPROVED,
        Proposal.PROCESSING_STATUS_DECLINED,
        Proposal.PROCESSING_STATUS_DISCARDED,
    ]

    # Delete ProposalParkActivity records that contain the removed activities
    proposal_parks = ProposalPark.objects.filter(park=instance).exclude(
        proposal__processing_status__in=exclude_statuses
    )
    proposal_park_activities = ProposalParkActivity.objects.filter(
        proposal_park__in=proposal_parks, activity__in=activities
    )
    if proposal_park_activities.exists():
        logger.info(
            f"Deleting ProposalParkActivity records for removed activities {activities} in park: {instance.name}"
        )
        proposal_park_activities.delete()

    # Remove the removed activities from ProposalEventsParks
    for eventPark in ProposalEventsParks.objects.filter(park=instance).exclude(
        proposal__processing_status__in=exclude_statuses
    ):
        removedActivities = eventPark.activities_assessor.filter(
            ~Q(id__in=instance.allowed_activities_ids)
        ).filter(id__in=pk_set)
        if not removedActivities.exists():
            continue
        logger.info(
            f"Removing ProposalEventsParks activities for removed activities {activities} in park: {instance.name}"
        )
        eventPark.activities_assessor.remove(*removedActivities)


@receiver(m2m_changed, sender=Trail.allowed_activities.through)
def handle_removed_trail_activities(sender, instance, **kwargs):
    post_remove = kwargs.get("action") == "post_remove"
    if not post_remove:
        return
    pk_set = kwargs.get("pk_set", [])
    activities = Activity.objects.filter(id__in=pk_set)

    from commercialoperator.components.proposals.models import (
        Proposal,
        ProposalTrail,
        ProposalTrailSectionActivity,
    )

    exclude_statuses = [
        Proposal.PROCESSING_STATUS_APPROVED,
        Proposal.PROCESSING_STATUS_DECLINED,
        Proposal.PROCESSING_STATUS_DISCARDED,
    ]

    proposal_trails = ProposalTrail.objects.filter(trail=instance).exclude(
        proposal__processing_status__in=exclude_statuses
    )
    proposal_trail_section_activities = ProposalTrailSectionActivity.objects.filter(
        trail_section__proposal_trail__in=proposal_trails, activity__in=activities
    )
    if proposal_trail_section_activities.exists():
        logger.info(
            f"Deleting ProposalTrailSectionActivity records for removed activities {activities} in trail: {instance.name}"
        )
        proposal_trail_section_activities.delete()


@receiver(m2m_changed, sender=Zone.allowed_activities.through)
def handle_remove_marine_zone_activities(sender, instance, **kwargs):
    post_remove = kwargs.get("action") == "post_remove"
    if not post_remove:
        return
    pk_set = kwargs.get("pk_set", [])
    activities = Activity.objects.filter(id__in=pk_set)

    from commercialoperator.components.proposals.models import (
        Proposal,
        ProposalPark,
        ProposalParkZoneActivity,
    )

    exclude_statuses = [
        Proposal.PROCESSING_STATUS_APPROVED,
        Proposal.PROCESSING_STATUS_DECLINED,
        Proposal.PROCESSING_STATUS_DISCARDED,
    ]

    proposal_parks = ProposalPark.objects.filter(park=instance.park).exclude(
        proposal__processing_status__in=exclude_statuses
    )
    proposal_park_activities = ProposalParkZoneActivity.objects.filter(
        park_zone__proposal_park__in=proposal_parks, activity__in=activities
    )
    if proposal_park_activities.exists():
        logger.info(
            f"Deleting ProposalParkZoneActivity records for removed activities {activities} in park: {instance.name}"
        )
        proposal_park_activities.delete()
