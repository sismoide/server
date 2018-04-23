from rest_framework.throttling import UserRateThrottle


class MobileThrottle(UserRateThrottle):
    scope = 'mobile'
