# -*- coding: utf-8 -*-
#
# REST Based Plugins - Unit Tests
#
# Copyright (C) 2017-2018 Chris Caron <lead2gold@gmail.com>
#
# This file is part of apprise.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

from apprise import plugins
from apprise import NotifyType
from apprise import Apprise
from apprise import AppriseAsset
from apprise.utils import compat_is_basestring
from json import dumps
import requests
import mock

TEST_URLS = (
    ##################################
    # NotifyBoxcar
    ##################################
    ('boxcar://', {
        'instance': None,
    }),
    # No secret specified
    ('boxcar://%s' % ('a' * 64), {
        'instance': None,
    }),
    # An invalid access and secret key specified
    ('boxcar://access.key/secret.key/', {
        # Thrown because there were no recipients specified
        'instance': TypeError,
    }),
    # Provide both an access and a secret
    ('boxcar://%s/%s' % ('a' * 64, 'b' * 64), {
        'instance': plugins.NotifyBoxcar,
        'requests_response_code': requests.codes.created,
    }),
    # Test without image set
    ('boxcar://%s/%s' % ('a' * 64, 'b' * 64), {
        'instance': plugins.NotifyBoxcar,
        'requests_response_code': requests.codes.created,
        # don't include an image by default
        'include_image': False,
    }),
    # our access, secret and device are all 64 characters
    # which is what we're doing here
    ('boxcar://%s/%s/@tag1/tag2///%s/' % (
        'a' * 64, 'b' * 64, 'd' * 64), {
        'instance': plugins.NotifyBoxcar,
        'requests_response_code': requests.codes.created,
    }),
    # An invalid tag
    ('boxcar://%s/%s/@%s' % ('a' * 64, 'b' * 64, 't' * 64), {
        'instance': plugins.NotifyBoxcar,
        'requests_response_code': requests.codes.created,
    }),
    ('boxcar://:@/', {
        'instance': None,
    }),
    ('boxcar://%s/%s/' % ('a' * 64, 'b' * 64), {
        'instance': plugins.NotifyBoxcar,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('boxcar://%s/%s/' % ('a' * 64, 'b' * 64), {
        'instance': plugins.NotifyBoxcar,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('boxcar://%s/%s/' % ('a' * 64, 'b' * 64), {
        'instance': plugins.NotifyBoxcar,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyDiscord
    ##################################
    ('discord://', {
        'instance': None,
    }),
    # No webhook_token specified
    ('discord://%s' % ('i' * 24), {
        'instance': TypeError,
    }),
    # Provide both an webhook id and a webhook token
    ('discord://%s/%s' % ('i' * 24, 't' * 64), {
        'instance': plugins.NotifyDiscord,
        'requests_response_code': requests.codes.no_content,
    }),
    # Provide a temporary username
    ('discord://l2g@%s/%s' % ('i' * 24, 't' * 64), {
        'instance': plugins.NotifyDiscord,
        'requests_response_code': requests.codes.no_content,
    }),
    # Enable other options
    ('discord://%s/%s?footer=Yes&thumbnail=Yes' % ('i' * 24, 't' * 64), {
        'instance': plugins.NotifyDiscord,
        'requests_response_code': requests.codes.no_content,
    }),
    ('discord://%s/%s?avatar=No&footer=No' % ('i' * 24, 't' * 64), {
        'instance': plugins.NotifyDiscord,
        'requests_response_code': requests.codes.no_content,
    }),
    # Test without image set
    ('discord://%s/%s' % ('i' * 24, 't' * 64), {
        'instance': plugins.NotifyDiscord,
        'requests_response_code': requests.codes.no_content,
        # don't include an image by default
        'include_image': False,
    }),
    # An invalid url
    ('discord://:@/', {
        'instance': None,
    }),
    ('discord://%s/%s/' % ('a' * 24, 'b' * 64), {
        'instance': plugins.NotifyDiscord,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('discord://%s/%s/' % ('a' * 24, 'b' * 64), {
        'instance': plugins.NotifyDiscord,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('discord://%s/%s/' % ('a' * 24, 'b' * 64), {
        'instance': plugins.NotifyDiscord,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyFaast
    ##################################
    ('faast://', {
        'instance': None,
    }),
    # Auth Token specified
    ('faast://%s' % ('a' * 32), {
        'instance': plugins.NotifyFaast,
    }),
    ('faast://%s' % ('a' * 32), {
        'instance': plugins.NotifyFaast,
        # don't include an image by default
        'include_image': False,
    }),
    ('faast://:@/', {
        'instance': None,
    }),
    ('faast://%s' % ('a' * 32), {
        'instance': plugins.NotifyFaast,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('faast://%s' % ('a' * 32), {
        'instance': plugins.NotifyFaast,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('faast://%s' % ('a' * 32), {
        'instance': plugins.NotifyFaast,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyJoin
    ##################################
    ('join://', {
        'instance': None,
    }),
    # APIkey; no device
    ('join://%s' % ('a' * 32), {
        'instance': plugins.NotifyJoin,
    }),
    # Invalid APIKey
    ('join://%s' % ('a' * 24), {
        # Missing a channel
        'instance': TypeError,
    }),
    # APIKey + device
    ('join://%s/%s' % ('a' * 32, 'd' * 32), {
        'instance': plugins.NotifyJoin,
        # don't include an image by default
        'include_image': False,
    }),
    # APIKey + 2 devices
    ('join://%s/%s/%s' % ('a' * 32, 'd' * 32, 'e' * 32), {
        'instance': plugins.NotifyJoin,
        # don't include an image by default
        'include_image': False,
    }),
    # APIKey + 1 device and 1 group
    ('join://%s/%s/%s' % ('a' * 32, 'd' * 32, 'group.chrome'), {
        'instance': plugins.NotifyJoin,
    }),
    # APIKey + bad device
    ('join://%s/%s' % ('a' * 32, 'd' * 10), {
        'instance': plugins.NotifyJoin,
    }),
    # APIKey + bad url
    ('join://:@/', {
        'instance': None,
    }),
    ('join://%s' % ('a' * 32), {
        'instance': plugins.NotifyJoin,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('join://%s' % ('a' * 32), {
        'instance': plugins.NotifyJoin,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('join://%s' % ('a' * 32), {
        'instance': plugins.NotifyJoin,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyJSON
    ##################################
    ('json://', {
        'instance': None,
    }),
    ('jsons://', {
        'instance': None,
    }),
    ('json://localhost', {
        'instance': plugins.NotifyJSON,
    }),
    ('json://user:pass@localhost', {
        'instance': plugins.NotifyJSON,
    }),
    ('json://localhost:8080', {
        'instance': plugins.NotifyJSON,
    }),
    ('json://user:pass@localhost:8080', {
        'instance': plugins.NotifyJSON,
    }),
    ('jsons://localhost', {
        'instance': plugins.NotifyJSON,
    }),
    ('jsons://user:pass@localhost', {
        'instance': plugins.NotifyJSON,
    }),
    ('jsons://localhost:8080/path/', {
        'instance': plugins.NotifyJSON,
    }),
    ('jsons://user:pass@localhost:8080', {
        'instance': plugins.NotifyJSON,
    }),
    ('json://:@/', {
        'instance': None,
    }),
    ('json://user:pass@localhost:8081', {
        'instance': plugins.NotifyJSON,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('json://user:pass@localhost:8082', {
        'instance': plugins.NotifyJSON,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('json://user:pass@localhost:8083', {
        'instance': plugins.NotifyJSON,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyKODI
    ##################################
    ('kodi://', {
        'instance': None,
    }),
    ('kodis://', {
        'instance': None,
    }),
    ('kodi://localhost', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodi://user:pass@localhost', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodi://localhost:8080', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodi://user:pass@localhost:8080', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodis://localhost', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodis://user:pass@localhost', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodis://localhost:8080/path/', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodis://user:pass@localhost:8080', {
        'instance': plugins.NotifyXBMC,
    }),
    ('kodi://localhost', {
        'instance': plugins.NotifyXBMC,
        # Experement with different notification types
        'notify_type': NotifyType.WARNING,
    }),
    ('kodi://localhost', {
        'instance': plugins.NotifyXBMC,
        # Experement with different notification types
        'notify_type': NotifyType.FAILURE,
    }),
    ('kodis://localhost:443', {
        'instance': plugins.NotifyXBMC,
        # don't include an image by default
        'include_image': False,
    }),
    ('kodi://:@/', {
        'instance': None,
    }),
    ('kodi://user:pass@localhost:8081', {
        'instance': plugins.NotifyXBMC,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('kodi://user:pass@localhost:8082', {
        'instance': plugins.NotifyXBMC,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('kodi://user:pass@localhost:8083', {
        'instance': plugins.NotifyXBMC,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyMatterMost
    ##################################
    ('mmost://', {
        'instance': None,
    }),
    ('mmosts://', {
        'instance': None,
    }),
    ('mmost://localhost/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
    }),
    ('mmost://user@localhost/3ccdd113474722377935511fc85d3dd4?channel=test', {
        'instance': plugins.NotifyMatterMost,
    }),
    ('mmost://localhost:8080/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
    }),
    ('mmost://localhost:0/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
    }),
    ('mmost://localhost:invalid-port/3ccdd113474722377935511fc85d3dd4', {
        'instance': None,
    }),
    ('mmosts://localhost/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
    }),
    ('mmosts://localhost', {
        # Thrown because there was no webhook id specified
        'instance': TypeError,
    }),
    ('mmost://localhost/bad-web-hook', {
        # Thrown because the webhook is not in a valid format
        'instance': TypeError,
    }),
    ('mmost://:@/', {
        'instance': None,
    }),
    ('mmost://localhost/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('mmost://localhost/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('mmost://localhost/3ccdd113474722377935511fc85d3dd4', {
        'instance': plugins.NotifyMatterMost,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyMyAndroid
    ##################################
    ('nma://', {
        'instance': None,
    }),
    # APIkey; no device
    ('nma://%s' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
    }),
    # Invalid APIKey
    ('nma://%s' % ('a' * 24), {
        'instance': TypeError,
    }),
    # APIKey
    ('nma://%s' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
        # don't include an image by default
        'include_image': False,
    }),
    # APIKey + priority setting
    ('nma://%s?priority=high' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
    }),
    # APIKey + invalid priority setting
    ('nma://%s?priority=invalid' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
    }),
    # APIKey + priority setting (empty)
    ('nma://%s?priority=' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
    }),
    # APIKey + Invalid DevAPI Key
    ('nma://%s/%s' % ('a' * 48, 'b' * 24), {
        'instance': TypeError,
    }),
    # APIKey + DevAPI Key
    ('nma://%s/%s' % ('a' * 48, 'b' * 48), {
        'instance': plugins.NotifyMyAndroid,
    }),
    # Testing valid format
    ('nma://%s?format=text' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
    }),
    # Testing valid format
    ('nma://%s?format=html' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
    }),
    # Testing invalid format (fall's back to html)
    ('nma://%s?format=invalid' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
    }),
    # Testing empty format (falls back to html)
    ('nma://%s?format=' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
    }),
    # APIKey + with image
    ('nma://%s' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
    }),
    # bad url
    ('nma://:@/', {
        'instance': None,
    }),
    ('nma://%s' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('nma://%s' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('nma://%s' % ('a' * 48), {
        'instance': plugins.NotifyMyAndroid,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyProwl
    ##################################
    ('prowl://', {
        'instance': None,
    }),
    # APIkey; no device
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # Invalid APIKey
    ('prowl://%s' % ('a' * 24), {
        'instance': TypeError,
    }),
    # APIKey
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
        # don't include an image by default
        'include_image': False,
    }),
    # APIKey + priority setting
    ('prowl://%s?priority=high' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # APIKey + invalid priority setting
    ('prowl://%s?priority=invalid' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # APIKey + priority setting (empty)
    ('prowl://%s?priority=' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # APIKey + Invalid Provider Key
    ('prowl://%s/%s' % ('a' * 40, 'b' * 24), {
        'instance': TypeError,
    }),
    # APIKey + No Provider Key (empty)
    ('prowl://%s///' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # APIKey + Provider Key
    ('prowl://%s/%s' % ('a' * 40, 'b' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # APIKey + with image
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
    }),
    # bad url
    ('prowl://:@/', {
        'instance': None,
    }),
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('prowl://%s' % ('a' * 40), {
        'instance': plugins.NotifyProwl,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyPushalot
    ##################################
    ('palot://', {
        'instance': None,
    }),
    # AuthToken
    ('palot://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushalot,
    }),
    # AuthToken, no image
    ('palot://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushalot,
        # don't include an image by default
        'include_image': False,
    }),
    # Invalid AuthToken
    ('palot://%s' % ('a' * 24), {
        # Missing a channel
        'instance': TypeError,
    }),
    # AuthToken + bad url
    ('palot://:@/', {
        'instance': None,
    }),
    ('palot://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushalot,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('palot://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushalot,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('palot://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushalot,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyPushBullet
    ##################################
    ('pbul://', {
        'instance': None,
    }),
    # APIkey
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
    }),
    # APIKey + channel
    ('pbul://%s/#channel/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
    }),
    # APIKey + 2 channels
    ('pbul://%s/#channel1/#channel2' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
    }),
    # APIKey + device
    ('pbul://%s/device/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
    }),
    # APIKey + 2 devices
    ('pbul://%s/device1/device2/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
    }),
    # APIKey + email
    ('pbul://%s/user@example.com/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
    }),
    # APIKey + 2 emails
    ('pbul://%s/user@example.com/abc@def.com/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
    }),
    # APIKey + Combo
    ('pbul://%s/device/#channel/user@example.com/' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
    }),
    # APIKey + bad url
    ('pbul://:@/', {
        'instance': None,
    }),
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('pbul://%s' % ('a' * 32), {
        'instance': plugins.NotifyPushBullet,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyPushover
    ##################################
    ('pover://', {
        'instance': None,
    }),
    # APIkey; no user
    ('pover://%s' % ('a' * 30), {
        'instance': TypeError,
    }),
    # APIkey; invalid user
    ('pover://%s@%s' % ('u' * 20, 'a' * 30), {
        'instance': TypeError,
    }),
    # Invalid APIKey; valid User
    ('pover://%s@%s' % ('u' * 30, 'a' * 24), {
        'instance': TypeError,
    }),
    # APIKey + Valid User
    ('pover://%s@%s' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
        # don't include an image by default
        'include_image': False,
    }),
    # APIKey + Valid User + 1 Device
    ('pover://%s@%s/DEVICE' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # APIKey + Valid User + 2 Devices
    ('pover://%s@%s/DEVICE1/DEVICE2/' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # APIKey + Valid User + invalid device
    ('pover://%s@%s/%s/' % ('u' * 30, 'a' * 30, 'd' * 30), {
        'instance': plugins.NotifyPushover,
        # Notify will return False since there is a bad device in our list
        'response': False,
    }),
    # APIKey + Valid User + device + invalid device
    ('pover://%s@%s/DEVICE1/%s/' % ('u' * 30, 'a' * 30, 'd' * 30), {
        'instance': plugins.NotifyPushover,
        # Notify will return False since there is a bad device in our list
        'response': False,
    }),
    # APIKey + priority setting
    ('pover://%s@%s?priority=high' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # APIKey + invalid priority setting
    ('pover://%s@%s?priority=invalid' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # APIKey + priority setting (empty)
    ('pover://%s@%s?priority=' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
    }),
    # bad url
    ('pover://:@/', {
        'instance': None,
    }),
    ('pover://%s@%s' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('pover://%s@%s' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('pover://%s@%s' % ('u' * 30, 'a' * 30), {
        'instance': plugins.NotifyPushover,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyRocketChat
    ##################################
    ('rocket://', {
        'instance': None,
    }),
    ('rockets://', {
        'instance': None,
    }),
    # No username or pass
    ('rocket://localhost', {
        'instance': TypeError,
    }),
    # No room or channel
    ('rocket://user:pass@localhost', {
        'instance': TypeError,
    }),
    # No valid rooms or channels
    ('rocket://user:pass@localhost/#/!/@', {
        'instance': TypeError,
    }),
    # A room and port identifier
    ('rocket://user:pass@localhost:8080/room/', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
    }),
    # A channel
    ('rockets://user:pass@localhost/#channel', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
    }),
    # Several channels
    ('rocket://user:pass@localhost/#channel1/#channel2/', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
    }),
    # Several Rooms
    ('rocket://user:pass@localhost/room1/room2', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
    }),
    # A room and channel
    ('rocket://user:pass@localhost/room/#channel', {
        'instance': plugins.NotifyRocketChat,
        # The response text is expected to be the following on a success
        'requests_response_text': {
            'status': 'success',
            'data': {
                'authToken': 'abcd',
                'userId': 'user',
            },
        },
    }),
    ('rocket://:@/', {
        'instance': None,
    }),
    # A room and channel
    ('rockets://user:pass@localhost/rooma/#channela', {
        # The response text is expected to be the following on a success
        'requests_response_code': requests.codes.ok,
        'requests_response_text': {
            # return something other then a success message type
            'status': 'failure',
        },
        # Exception is thrown in this case
        'instance': plugins.NotifyRocketChat,
        # Notifications will fail in this event
        'response': False,
    }),
    ('rocket://user:pass@localhost:8081/room1/room2', {
        'instance': plugins.NotifyRocketChat,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('rocket://user:pass@localhost:8082/#channel', {
        'instance': plugins.NotifyRocketChat,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('rocket://user:pass@localhost:8083/#chan1/#chan2/room', {
        'instance': plugins.NotifyRocketChat,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifySlack
    ##################################
    ('slack://', {
        'instance': None,
    }),
    ('slack://:@/', {
        'instance': None,
    }),
    ('slack://T1JJ3T3L2', {
        # Just Token 1 provided
        'instance': None,
    }),
    ('slack://T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#hmm/#-invalid-', {
        # No username specified; this is still okay as we sub in
        # default; The one invalid channel is skipped when sending a message
        'instance': plugins.NotifySlack,
    }),
    ('slack://T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#channel', {
        # No username specified; this is still okay as we sub in
        # default; The one invalid channel is skipped when sending a message
        'instance': plugins.NotifySlack,
        # don't include an image by default
        'include_image': False,
    }),
    ('slack://T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/+id/%20/@id/', {
        # + encoded id,
        # @ userid
        'instance': plugins.NotifySlack,
    }),
    ('slack://username@T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#nuxref', {
        'instance': plugins.NotifySlack,
    }),
    ('slack://username@T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ', {
        # Missing a channel
        'instance': TypeError,
    }),
    ('slack://username@INVALID/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#cool', {
        # invalid 1st Token
        'instance': TypeError,
    }),
    ('slack://username@T1JJ3T3L2/INVALID/TIiajkdnlazkcOXrIdevi7FQ/#great', {
        # invalid 2rd Token
        'instance': TypeError,
    }),
    ('slack://username@T1JJ3T3L2/A1BRTD4JD/INVALID/#channel', {
        # invalid 3rd Token
        'instance': TypeError,
    }),
    ('slack://l2g@T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#usenet', {
        'instance': plugins.NotifySlack,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('slack://respect@T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#a', {
        'instance': plugins.NotifySlack,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('slack://notify@T1JJ3T3L2/A1BRTD4JD/TIiajkdnlazkcOXrIdevi7FQ/#b', {
        'instance': plugins.NotifySlack,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyTelegram
    ##################################
    ('tgram://', {
        'instance': None,
    }),
    # Simple Message
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
    }),
    # Simple Message (no images)
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # don't include an image by default
        'include_image': False,
    }),
    # Simple Message with multiple chat names
    ('tgram://123456789:abcdefg_hijklmnop/id1/id2/', {
        'instance': plugins.NotifyTelegram,
    }),
    # Simple Message with an invalid chat ID
    ('tgram://123456789:abcdefg_hijklmnop/%$/', {
        'instance': plugins.NotifyTelegram,
        # Notify will fail
        'response': False,
    }),
    # Simple Message with multiple chat ids
    ('tgram://123456789:abcdefg_hijklmnop/id1/id2/23423/-30/', {
        'instance': plugins.NotifyTelegram,
    }),
    # Simple Message with multiple chat ids (no images)
    ('tgram://123456789:abcdefg_hijklmnop/id1/id2/23423/-30/', {
        'instance': plugins.NotifyTelegram,
        # don't include an image by default
        'include_image': False,
    }),
    # Support bot keyword prefix
    ('tgram://bottest@123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
    }),
    # Testing image
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?image=Yes', {
        'instance': plugins.NotifyTelegram,
    }),
    # Testing invalid format (fall's back to html)
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?format=invalid', {
        'instance': plugins.NotifyTelegram,
    }),
    # Testing empty format (falls back to html)
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?format=', {
        'instance': plugins.NotifyTelegram,
    }),
    # Simple Message without image
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # don't include an image by default
        'include_image': False,
    }),
    # Invalid Bot Token
    ('tgram://alpha:abcdefg_hijklmnop/lead2gold/', {
        'instance': None,
    }),
    # AuthToken + bad url
    ('tgram://:@/', {
        'instance': None,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?image=Yes', {
        'instance': plugins.NotifyTelegram,
        # force a failure without an image specified
        'include_image': False,
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/id1/id2/', {
        'instance': plugins.NotifyTelegram,
        # force a failure with multiple chat_ids
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/id1/id2/', {
        'instance': plugins.NotifyTelegram,
        # force a failure without an image specified
        'include_image': False,
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # throw a bizzare code forcing us to fail to look it up without
        # having an image included
        'include_image': False,
        'response': False,
        'requests_response_code': 999,
    }),
    # Test with image set
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?image=Yes', {
        'instance': plugins.NotifyTelegram,
        # throw a bizzare code forcing us to fail to look it up without
        # having an image included
        'include_image': True,
        'response': False,
        'requests_response_code': 999,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/', {
        'instance': plugins.NotifyTelegram,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),
    ('tgram://123456789:abcdefg_hijklmnop/lead2gold/?image=Yes', {
        'instance': plugins.NotifyTelegram,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them without images set
        'include_image': True,
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyToasty (SuperToasty)
    ##################################
    ('toasty://', {
        'instance': None,
    }),
    # No username specified but contains a device
    ('toasty://%s' % ('d' * 32), {
        'instance': TypeError,
    }),
    # User + 1 device
    ('toasty://user@device', {
        'instance': plugins.NotifyToasty,
    }),
    # User + 3 devices
    ('toasty://user@device0/device1/device2/', {
        'instance': plugins.NotifyToasty,
        # don't include an image by default
        'include_image': False,
    }),
    # bad url
    ('toasty://:@/', {
        'instance': None,
    }),
    ('toasty://user@device', {
        'instance': plugins.NotifyToasty,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('toasty://user@device', {
        'instance': plugins.NotifyToasty,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('toasty://user@device', {
        'instance': plugins.NotifyToasty,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyKODI
    ##################################
    ('xbmc://', {
        'instance': None,
    }),
    ('xbmc://localhost', {
        'instance': plugins.NotifyXBMC,
    }),
    ('xbmc://user:pass@localhost', {
        'instance': plugins.NotifyXBMC,
    }),
    ('xbmc://localhost:8080', {
        'instance': plugins.NotifyXBMC,
    }),
    ('xbmc://user:pass@localhost:8080', {
        'instance': plugins.NotifyXBMC,
    }),
    ('xbmc://localhost', {
        'instance': plugins.NotifyXBMC,
        # don't include an image by default
        'include_image': False,
    }),
    ('xbmc://localhost', {
        'instance': plugins.NotifyXBMC,
        # Experement with different notification types
        'notify_type': NotifyType.WARNING,
    }),
    ('xbmc://localhost', {
        'instance': plugins.NotifyXBMC,
        # Experement with different notification types
        'notify_type': NotifyType.FAILURE,
    }),
    ('xbmc://:@/', {
        'instance': None,
    }),
    ('xbmc://user:pass@localhost:8081', {
        'instance': plugins.NotifyXBMC,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('xbmc://user:pass@localhost:8082', {
        'instance': plugins.NotifyXBMC,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('xbmc://user:pass@localhost:8083', {
        'instance': plugins.NotifyXBMC,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),

    ##################################
    # NotifyXML
    ##################################
    ('xml://', {
        'instance': None,
    }),
    ('xmls://', {
        'instance': None,
    }),
    ('xml://localhost', {
        'instance': plugins.NotifyXML,
    }),
    ('xml://user:pass@localhost', {
        'instance': plugins.NotifyXML,
    }),
    ('xml://localhost:8080', {
        'instance': plugins.NotifyXML,
    }),
    ('xml://user:pass@localhost:8080', {
        'instance': plugins.NotifyXML,
    }),
    ('xmls://localhost', {
        'instance': plugins.NotifyXML,
    }),
    ('xmls://user:pass@localhost', {
        'instance': plugins.NotifyXML,
    }),
    ('xmls://localhost:8080/path/', {
        'instance': plugins.NotifyXML,
    }),
    ('xmls://user:pass@localhost:8080', {
        'instance': plugins.NotifyXML,
    }),
    ('xml://:@/', {
        'instance': None,
    }),
    ('xml://user:pass@localhost:8081', {
        'instance': plugins.NotifyXML,
        # force a failure
        'response': False,
        'requests_response_code': requests.codes.internal_server_error,
    }),
    ('xml://user:pass@localhost:8082', {
        'instance': plugins.NotifyXML,
        # throw a bizzare code forcing us to fail to look it up
        'response': False,
        'requests_response_code': 999,
    }),
    ('xml://user:pass@localhost:8083', {
        'instance': plugins.NotifyXML,
        # Throws a series of connection and transfer exceptions when this flag
        # is set and tests that we gracfully handle them
        'test_requests_exceptions': True,
    }),
)


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_rest_plugins(mock_post, mock_get):
    """
    API: REST Based Plugins()

    """

    # iterate over our dictionary and test it out
    for (url, meta) in TEST_URLS:

        # Our expected instance
        instance = meta.get('instance', None)

        # Our expected server objects
        self = meta.get('self', None)

        # Our expected Query response (True, False, or exception type)
        response = meta.get('response', True)

        # Allow us to force the server response code to be something other then
        # the defaults
        requests_response_code = meta.get(
            'requests_response_code',
            requests.codes.ok if response else requests.codes.not_found,
        )

        # Allow us to force the server response text to be something other then
        # the defaults
        requests_response_text = meta.get('requests_response_text')
        if not compat_is_basestring(requests_response_text):
            # Convert to string
            requests_response_text = dumps(requests_response_text)

        # Allow notification type override, otherwise default to INFO
        notify_type = meta.get('notify_type', NotifyType.INFO)

        # Whether or not we should include an image with our request; unless
        # otherwise specified, we assume that images are to be included
        include_image = meta.get('include_image', True)
        if include_image:
            # a default asset
            asset = AppriseAsset()

        else:
            # Disable images
            asset = AppriseAsset(image_path_mask=False, image_url_mask=False)

        test_requests_exceptions = meta.get(
            'test_requests_exceptions', False)

        # A request
        robj = mock.Mock()
        setattr(robj, 'raw', mock.Mock())
        # Allow raw.read() calls
        robj.raw.read.return_value = ''
        mock_get.return_value = robj
        mock_post.return_value = robj

        if test_requests_exceptions is False:
            # Handle our default response
            mock_post.return_value.status_code = requests_response_code
            mock_get.return_value.status_code = requests_response_code

            # Handle our default text response
            mock_get.return_value.text = requests_response_text
            mock_post.return_value.text = requests_response_text

            # Ensure there is no side effect set
            mock_post.side_effect = None
            mock_get.side_effect = None

        else:
            # Handle exception testing; first we turn the boolean flag ito
            # a list of exceptions
            test_requests_exceptions = (
                requests.ConnectionError(
                    0, 'requests.ConnectionError() not handled'),
                requests.RequestException(
                    0, 'requests.RequestException() not handled'),
                requests.HTTPError(
                    0, 'requests.HTTPError() not handled'),
                requests.ReadTimeout(
                    0, 'requests.ReadTimeout() not handled'),
                requests.TooManyRedirects(
                    0, 'requests.TooManyRedirects() not handled'),
            )

        try:
            obj = Apprise.instantiate(
                url, asset=asset, suppress_exceptions=False)

            if obj is None:
                # We're done (assuming this is what we were expecting)
                assert instance is None
                continue

            assert(isinstance(obj, instance))

            # Disable throttling to speed up unit tests
            obj.throttle_attempt = 0

            if self:
                # Iterate over our expected entries inside of our object
                for key, val in self.items():
                    # Test that our object has the desired key
                    assert(hasattr(key, obj))
                    assert(getattr(key, obj) == val)

            try:
                if test_requests_exceptions is False:
                    # check that we're as expected
                    assert obj.notify(
                        title='test', body='body',
                        notify_type=notify_type) == response

                else:
                    for _exception in test_requests_exceptions:
                        mock_post.side_effect = _exception
                        mock_get.side_effect = _exception

                        try:
                            assert obj.notify(
                                title='test', body='body',
                                notify_type=NotifyType.INFO) is False

                        except AssertionError:
                            # Don't mess with these entries
                            raise

                        except Exception as e:
                            # We can't handle this exception type
                            print('%s / %s' % (url, str(e)))
                            assert False

            except AssertionError:
                # Don't mess with these entries
                print('%s AssertionError' % url)
                raise

            except Exception as e:
                # Check that we were expecting this exception to happen
                assert isinstance(e, response)

        except AssertionError:
            # Don't mess with these entries
            print('%s AssertionError' % url)
            raise

        except Exception as e:
            # Handle our exception
            print('%s / %s' % (url, str(e)))
            assert(instance is not None)
            assert(isinstance(e, instance))


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_boxcar_plugin(mock_post, mock_get):
    """
    API: NotifyBoxcar() Extra Checks

    """
    # Generate some generic message types
    device = 'A' * 64
    tag = '@B' * 63

    access = '-' * 64
    secret = '_' * 64

    # Initializes the plugin with recipients set to None
    plugins.NotifyBoxcar(access=access, secret=secret, recipients=None)

    # Initializes the plugin with a valid access, but invalid access key
    try:
        plugins.NotifyBoxcar(access=None, secret=secret, recipients=None)
        assert(False)

    except TypeError:
        # We should throw an exception for knowingly having an invalid
        assert(True)

    # Initializes the plugin with a valid access, but invalid secret key
    try:
        plugins.NotifyBoxcar(access=access, secret='invalid', recipients=None)
        assert(False)

    except TypeError:
        # We should throw an exception for knowingly having an invalid key
        assert(True)

    # Initializes the plugin with a valid access, but invalid secret
    try:
        plugins.NotifyBoxcar(access=access, secret=None, recipients=None)
        assert(False)

    except TypeError:
        # We should throw an exception for knowingly having an invalid
        assert(True)

    # Initializes the plugin with recipients list
    # the below also tests our the variation of recipient types
    plugins.NotifyBoxcar(
        access=access, secret=secret, recipients=[device, tag])

    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.created
    mock_get.return_value.status_code = requests.codes.created

    # Test notifications without a body or a title
    p = plugins.NotifyBoxcar(access=access, secret=secret, recipients=None)

    # Disable throttling to speed up unit tests
    p.throttle_attempt = 0

    p.notify(body=None, title=None, notify_type=NotifyType.INFO) is True


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_discord_plugin(mock_post, mock_get):
    """
    API: NotifyDiscord() Extra Checks

    """

    # Initialize some generic (but valid) tokens
    webhook_id = 'A' * 24
    webhook_token = 'B' * 64

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok

    # Empty Channel list
    try:
        plugins.NotifyDiscord(webhook_id=None, webhook_token=webhook_token)
        assert(False)

    except TypeError:
        # we'll thrown because no webhook_id was specified
        assert(True)

    obj = plugins.NotifyDiscord(
        webhook_id=webhook_id,
        webhook_token=webhook_token,
        footer=True, thumbnail=False)

    # Disable throttling to speed up unit tests
    obj.throttle_attempt = 0

    # This call includes an image with it's payload:
    assert obj.notify(title='title', body='body',
                      notify_type=NotifyType.INFO) is True

    # Toggle our logo availability
    obj.asset.image_url_logo = None
    assert obj.notify(title='title', body='body',
                      notify_type=NotifyType.INFO) is True


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_join_plugin(mock_post, mock_get):
    """
    API: NotifyJoin() Extra Checks

    """
    # Generate some generic message types
    device = 'A' * 32
    group = 'group.chrome'
    apikey = 'a' * 32

    # Initializes the plugin with devices set to a string
    plugins.NotifyJoin(apikey=apikey, devices=group)

    # Initializes the plugin with devices set to None
    plugins.NotifyJoin(apikey=apikey, devices=None)

    # Initializes the plugin with devices set to a set
    p = plugins.NotifyJoin(apikey=apikey, devices=[group, device])

    # Prepare our mock responses
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.created
    mock_get.return_value.status_code = requests.codes.created

    # Disable throttling to speed up unit tests
    p.throttle_attempt = 0

    # Test notifications without a body or a title; nothing to send
    # so we return False
    p.notify(body=None, title=None, notify_type=NotifyType.INFO) is False


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_slack_plugin(mock_post, mock_get):
    """
    API: NotifySlack() Extra Checks

    """

    # Initialize some generic (but valid) tokens
    token_a = 'A' * 9
    token_b = 'B' * 9
    token_c = 'c' * 24

    # Support strings
    channels = 'chan1,#chan2,+id,@user,,,'

    obj = plugins.NotifySlack(
        token_a=token_a, token_b=token_b, token_c=token_c, channels=channels)
    assert(len(obj.channels) == 4)

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok

    # Empty Channel list
    try:
        plugins.NotifySlack(
            token_a=token_a, token_b=token_b, token_c=token_c,
            channels=None)
        assert(False)

    except TypeError:
        # we'll thrown because an empty list of channels was provided
        assert(True)

    # Test include_image
    obj = plugins.NotifySlack(
        token_a=token_a, token_b=token_b, token_c=token_c, channels=channels,
        include_image=True)

    # Disable throttling to speed up unit tests
    obj.throttle_attempt = 0

    # This call includes an image with it's payload:
    assert obj.notify(title='title', body='body',
                      notify_type=NotifyType.INFO) is True


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_pushbullet_plugin(mock_post, mock_get):
    """
    API: NotifyPushBullet() Extra Checks

    """

    # Initialize some generic (but valid) tokens
    accesstoken = 'a' * 32

    # Support strings
    recipients = '#chan1,#chan2,device,user@example.com,,,'

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok

    obj = plugins.NotifyPushBullet(
        accesstoken=accesstoken, recipients=recipients)
    assert(isinstance(obj, plugins.NotifyPushBullet))
    assert(len(obj.recipients) == 4)

    obj = plugins.NotifyPushBullet(accesstoken=accesstoken)
    assert(isinstance(obj, plugins.NotifyPushBullet))
    # Default is to send to all devices, so there will be a
    # recipient here
    assert(len(obj.recipients) == 1)

    obj = plugins.NotifyPushBullet(accesstoken=accesstoken, recipients=set())
    assert(isinstance(obj, plugins.NotifyPushBullet))
    # Default is to send to all devices, so there will be a
    # recipient here
    assert(len(obj.recipients) == 1)

    # Support the handling of an empty and invalid URL strings
    assert(plugins.NotifyPushBullet.parse_url(None) is None)
    assert(plugins.NotifyPushBullet.parse_url('') is None)
    assert(plugins.NotifyPushBullet.parse_url(42) is None)


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_pushover_plugin(mock_post, mock_get):
    """
    API: NotifyPushover() Extra Checks

    """

    # Initialize some generic (but valid) tokens
    token = 'a' * 30
    user = 'u' * 30

    invalid_device = 'd' * 35

    # Support strings
    devices = 'device1,device2,,,,%s' % invalid_device

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok

    try:
        obj = plugins.NotifyPushover(user=user, token=None)
        # No token specified
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no token was specified
        assert(True)

    obj = plugins.NotifyPushover(user=user, token=token, devices=devices)
    assert(isinstance(obj, plugins.NotifyPushover))
    assert(len(obj.devices) == 3)

    # Disable throttling to speed up unit tests
    obj.throttle_attempt = 0

    # This call fails because there is 1 invalid device
    assert obj.notify(title='title', body='body',
                      notify_type=NotifyType.INFO) is False

    obj = plugins.NotifyPushover(user=user, token=token)
    assert(isinstance(obj, plugins.NotifyPushover))
    # Default is to send to all devices, so there will be a
    # device defined here
    assert(len(obj.devices) == 1)

    # Disable throttling to speed up unit tests
    obj.throttle_attempt = 0

    # This call succeeds because all of the devices are valid
    assert obj.notify(title='title', body='body',
                      notify_type=NotifyType.INFO) is True

    obj = plugins.NotifyPushover(user=user, token=token, devices=set())
    assert(isinstance(obj, plugins.NotifyPushover))
    # Default is to send to all devices, so there will be a
    # device defined here
    assert(len(obj.devices) == 1)

    # Support the handling of an empty and invalid URL strings
    assert(plugins.NotifyPushover.parse_url(None) is None)
    assert(plugins.NotifyPushover.parse_url('') is None)
    assert(plugins.NotifyPushover.parse_url(42) is None)


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_rocketchat_plugin(mock_post, mock_get):
    """
    API: NotifyRocketChat() Extra Checks

    """
    # Chat ID
    recipients = 'l2g, lead2gold, #channel, #channel2'

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok
    mock_post.return_value.text = ''
    mock_get.return_value.text = ''

    try:
        obj = plugins.NotifyRocketChat(recipients=None)
        # invalid recipients list (None)
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no recipients were
        # specified
        assert(True)

    try:
        obj = plugins.NotifyRocketChat(recipients=object())
        # invalid recipients list (object)
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no recipients were
        # specified
        assert(True)

    try:
        obj = plugins.NotifyRocketChat(recipients=set())
        # invalid recipient list/set (no entries)
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no recipients were
        # specified
        assert(True)

    obj = plugins.NotifyRocketChat(recipients=recipients)
    assert(isinstance(obj, plugins.NotifyRocketChat))
    assert(len(obj.channels) == 2)
    assert(len(obj.rooms) == 2)

    # Disable throttling to speed up unit tests
    obj.throttle_attempt = 0

    #
    # Logout
    #
    assert obj.logout() is True

    # Support the handling of an empty and invalid URL strings
    assert plugins.NotifyRocketChat.parse_url(None) is None
    assert plugins.NotifyRocketChat.parse_url('') is None
    assert plugins.NotifyRocketChat.parse_url(42) is None

    # Prepare Mock to fail
    mock_post.return_value.status_code = requests.codes.internal_server_error
    mock_get.return_value.status_code = requests.codes.internal_server_error
    mock_post.return_value.text = ''
    mock_get.return_value.text = ''

    #
    # Send Notification
    #
    assert obj.notify(
        title='title', body='body', notify_type=NotifyType.INFO) is False
    assert obj.send_notification(
        payload='test', notify_type=NotifyType.INFO) is False

    #
    # Logout
    #
    assert obj.logout() is False

    # KeyError handling
    mock_post.return_value.status_code = 999
    mock_get.return_value.status_code = 999

    #
    # Send Notification
    #
    assert obj.notify(
        title='title', body='body', notify_type=NotifyType.INFO) is False
    assert obj.send_notification(
        payload='test', notify_type=NotifyType.INFO) is False

    #
    # Logout
    #
    assert obj.logout() is False

    mock_post.return_value.text = ''
    # Generate exceptions
    mock_get.side_effect = requests.ConnectionError(
        0, 'requests.ConnectionError() not handled')
    mock_post.side_effect = mock_get.side_effect
    mock_get.return_value.text = ''
    mock_post.return_value.text = ''

    #
    # Send Notification
    #
    assert obj.send_notification(
        payload='test', notify_type=NotifyType.INFO) is False

    # Attempt the check again but fake a successful login
    obj.login = mock.Mock()
    obj.login.return_value = True
    assert obj.notify(
        title='title', body='body', notify_type=NotifyType.INFO) is False
    #
    # Logout
    #
    assert obj.logout() is False


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_toasty_plugin(mock_post, mock_get):
    """
    API: NotifyToasty() Extra Checks

    """

    # Support strings
    devices = 'device1,device2,,,,'

    # User
    user = 'l2g'

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok

    try:
        obj = plugins.NotifyToasty(user=user, devices=None)
        # No devices specified
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no token was specified
        assert(True)

    try:
        obj = plugins.NotifyToasty(user=user, devices=set())
        # No devices specified
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no token was specified
        assert(True)

    obj = plugins.NotifyToasty(user=user, devices=devices)
    assert(isinstance(obj, plugins.NotifyToasty))
    assert(len(obj.devices) == 2)

    # Support the handling of an empty and invalid URL strings
    assert(plugins.NotifyToasty.parse_url(None) is None)
    assert(plugins.NotifyToasty.parse_url('') is None)
    assert(plugins.NotifyToasty.parse_url(42) is None)


@mock.patch('requests.get')
@mock.patch('requests.post')
def test_notify_telegram_plugin(mock_post, mock_get):
    """
    API: NotifyTelegram() Extra Checks

    """
    # Bot Token
    bot_token = '123456789:abcdefg_hijklmnop'
    invalid_bot_token = 'abcd:123'

    # Chat ID
    chat_ids = 'l2g, lead2gold'

    # Prepare Mock
    mock_get.return_value = requests.Request()
    mock_post.return_value = requests.Request()
    mock_post.return_value.status_code = requests.codes.ok
    mock_get.return_value.status_code = requests.codes.ok
    mock_get.return_value.content = '{}'
    mock_post.return_value.content = '{}'

    try:
        obj = plugins.NotifyTelegram(bot_token=None, chat_ids=chat_ids)
        # invalid bot token (None)
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no token was specified
        assert(True)

    try:
        obj = plugins.NotifyTelegram(
            bot_token=invalid_bot_token, chat_ids=chat_ids)
        # invalid bot token
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact an invalid token was
        # specified
        assert(True)

    try:
        obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids=None)
        # No chat_ids specified
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no token was specified
        assert(True)

    try:
        obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids=set())
        # No chat_ids specified
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no token was specified
        assert(True)

    obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids=chat_ids)
    assert(isinstance(obj, plugins.NotifyTelegram))
    assert(len(obj.chat_ids) == 2)

    # Support the handling of an empty and invalid URL strings
    assert(plugins.NotifyTelegram.parse_url(None) is None)
    assert(plugins.NotifyTelegram.parse_url('') is None)
    assert(plugins.NotifyTelegram.parse_url(42) is None)

    # Prepare Mock to fail
    response = mock.Mock()
    response.status_code = requests.codes.internal_server_error

    # a error response
    response.text = dumps({
        'description': 'test',
    })
    mock_get.return_value = response
    mock_post.return_value = response

    # No image asset
    nimg_obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids=chat_ids)
    nimg_obj.asset = AppriseAsset(image_path_mask=False, image_url_mask=False)

    # Disable throttling to speed up unit tests
    nimg_obj.throttle_attempt = 0
    obj.throttle_attempt = 0

    # This tests erroneous messages involving multiple chat ids
    assert obj.notify(
        title='title', body='body', notify_type=NotifyType.INFO) is False
    assert nimg_obj.notify(
        title='title', body='body', notify_type=NotifyType.INFO) is False

    # This tests erroneous messages involving a single chat id
    obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids='l2g')
    nimg_obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids='l2g')
    nimg_obj.asset = AppriseAsset(image_path_mask=False, image_url_mask=False)

    assert obj.notify(
        title='title', body='body', notify_type=NotifyType.INFO) is False
    assert nimg_obj.notify(
        title='title', body='body', notify_type=NotifyType.INFO) is False

    # Bot Token Detection
    # Just to make it clear to people reading this code and trying to learn
    # what is going on.  Apprise tries to detect the bot owner if you don't
    # specify a user to message.  The idea is to just default to messaging
    # the bot owner himself (it makes it easier for people).  So we're testing
    # the creating of a Telegram Notification without providing a chat ID.
    # We're testing the error handling of this bot detection section of the
    # code
    mock_post.return_value.content = dumps({
        "ok": True,
        "result": [{
            "update_id": 645421321,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 532389719,
                    "is_bot": False,
                    "first_name": "Chris",
                    "language_code": "en-US"
                },
                "chat": {
                    "id": 532389719,
                    "first_name": "Chris",
                    "type": "private"
                },
                "date": 1519694394,
                "text": "/start",
                "entities": [{
                    "offset": 0,
                    "length": 6,
                    "type": "bot_command",
                }],
            }},
        ],
    })
    mock_post.return_value.status_code = requests.codes.ok

    obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids=None)
    assert(len(obj.chat_ids) == 1)
    assert(obj.chat_ids[0] == '532389719')

    # Do the test again, but without the expected (parsed response)
    mock_post.return_value.content = dumps({
        "ok": True,
        "result": [{
            "message": {
                "text": "/ignored.entry",
            }},
        ],
    })
    try:
        obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids=None)
        # No chat_ids specified
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no token was specified
        assert(True)

    # Test our bot detection with a internal server error
    mock_post.return_value.status_code = requests.codes.internal_server_error
    try:
        obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids=None)
        # No chat_ids specified
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no token was specified
        assert(True)

    # Test our bot detection with an unmappable html error
    mock_post.return_value.status_code = 999
    try:
        obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids=None)
        # No chat_ids specified
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no token was specified
        assert(True)

    # Do it again but this time provide a failure message
    mock_post.return_value.content = dumps({'description': 'Failure Message'})
    try:
        obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids=None)
        # No chat_ids specified
        assert(False)

    except TypeError:
        # Exception should be thrown about the fact no token was specified
        assert(True)

    # Do it again but this time provide a failure message and perform a
    # notification without a bot detection by providing at least 1 chat id
    obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids=['@abcd'])
    assert nimg_obj.notify(
        title='title', body='body', notify_type=NotifyType.INFO) is False

    # Test our exception handling with bot detection
    test_requests_exceptions = (
        requests.ConnectionError(
            0, 'requests.ConnectionError() not handled'),
        requests.RequestException(
            0, 'requests.RequestException() not handled'),
        requests.HTTPError(
            0, 'requests.HTTPError() not handled'),
        requests.ReadTimeout(
            0, 'requests.ReadTimeout() not handled'),
        requests.TooManyRedirects(
            0, 'requests.TooManyRedirects() not handled'),
    )

    # iterate over our exceptions and test them
    for _exception in test_requests_exceptions:
        mock_post.side_effect = _exception
        try:
            obj = plugins.NotifyTelegram(bot_token=bot_token, chat_ids=None)
            # No chat_ids specified
            assert(False)

        except TypeError:
            # Exception should be thrown about the fact no token was specified
            assert(True)