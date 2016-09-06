from tastypie.throttle import CacheDBThrottle
import time
from django.core.cache import cache
from django.contrib.auth.models import User, SiteProfileNotAvailable

import logging
log = logging.getLogger(__name__)

class UserAccessThrottle(CacheDBThrottle):
    """
    A throttling mechanism that uses the cache for actual throttling but
    writes-through to the database.

    This is useful for tracking/aggregating usage through time, to possibly
    build a statistics interface or a billing mechanism.
    """
    def __init__(self, throttle_at=150, timeframe=3600, expiration=None, model_type=None):
        super(UserAccessThrottle, self).__init__(throttle_at,timeframe,expiration)
        self.model_type = model_type

    def should_be_throttled(self, identifier, **kwargs):
        """
        Returns whether or not the user has exceeded their throttle limit.

        Maintains a list of timestamps when the user accessed the api within
        the cache.

        Returns ``False`` if the user should NOT be throttled or ``True`` if
        the user should be throttled.
        """

        #Generate a more granular id
        new_id, url, request_method = self.get_new_id(identifier, **kwargs)
        key = self.convert_identifier_to_key(new_id)

        #See if we can get a user and adjust throttle limit
        user = self.get_user(identifier)
        throttle_at = self.get_rate_limit_for_user(user)

        # Make sure something is there.
        cache.add(key, [])

        # Weed out anything older than the timeframe.
        minimum_time = int(time.time()) - int(self.timeframe)
        times_accessed = [access for access in cache.get(key) if access >= minimum_time]
        cache.set(key, times_accessed, self.expiration)

        if len(times_accessed) >= int(throttle_at):
            # Throttle them.
            return True

        # Let them through.
        return False

    def accessed(self, identifier, **kwargs):
        """
        Handles recording the user's access.
        identifier - whatever identifier is passed into the class.  Generally the username
        kwargs - can contain request method and url
        """

        #Generate a new id
        new_id, url, request_method = self.get_new_id(identifier, **kwargs)
        key = self.convert_identifier_to_key(new_id)

        #Get times accessed and increment
        times_accessed = cache.get(key, [])
        times_accessed.append(int(time.time()))
        cache.set(key, times_accessed, self.expiration)

        # Write out the access to the DB for logging purposes.
        # Do the import here, instead of top-level, so that the model is
        # only required when using this throttling mechanism.
        from tastypie.models import ApiAccess
        ApiAccess.objects.create(
            identifier=identifier,
            url=url,
            request_method=request_method,
        )

    def get_new_id(self, identifier, **kwargs):
        """
        Generates a new, more granular, identifier, and parses request method and url from kwargs
        identifier - whatever identifier is passed into the class.  Generally the username
        kwargs - can contain request method and url
        """
        url = kwargs.get('url', '')
        request_method = kwargs.get('request_method', '')
        new_id = "{0}.{1}.{2}".format(identifier,url,request_method)
        return new_id, url, request_method

    def get_user(self, identifier):
        """
        Try to get a user object from the identifier
        identifier - whatever identifier is passed into the class.  Generally the username
        """
        try:
            user = User.objects.get(username=identifier)
        except:
            user = None

        return user

    def get_rate_limit_for_user(self, user):
        """
        See if the user has a higher rate limit than the global throttle setting
        user - a user object
        """
        throttle_at = self.throttle_at
        if user is not None:
            try:
                profile = user.profile
            except SiteProfileNotAvailable:
                log.warn("No user profile available for {0}".format(user.username))
                return throttle_at
            if user.profile.throttle_at > throttle_at:
                throttle_at = user.throttle_at
        return throttle_at
