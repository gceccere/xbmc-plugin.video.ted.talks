
import re
# Custom xbmc thing for fast parsing. Can't rely on lxml being available as of 2012-03.
import CommonFunctions as xbmc_common
import httplib
import urlparse

__download_link_re = re.compile('http://download.ted.com/talks/.+.mp4')

def get(html, video_quality=3):
    """Extract talk details from talk html
       @param video_quality 1-7 with 7 being highest. 3 = standard.
    """

    headline = xbmc_common.parseDOM(html, 'span', attrs={'id':'altHeadline'})[0].split(':', 1)
    speaker = headline[0].strip()
    title = headline[1].strip()
    plot = xbmc_common.parseDOM(html, 'p', attrs={'id':'tagline'})[0]

    url = None
    for link in xbmc_common.parseDOM(html, 'a', ret='href'):
        if __download_link_re.match(link):
            url = link
            break

    # We could confirm these URLs exist from the DOM (with difficulty) but seems likely to break
    if url and not video_quality == 3:
        # Quality '42' for testing
        video_quality_string = {1:'64', 2:'180', 4:'450', 5:'600', 6:'950', 7:'1500', 42:'42'}[video_quality]
        url_custom = url.replace(".mp4", "-%sk.mp4" % (video_quality_string))

        # Test URL exists
        url_custom_parsed = urlparse.urlparse(url_custom)
        h = httplib.HTTPConnection(url_custom_parsed.netloc)
        h.request('HEAD', url_custom_parsed.path)
        response = h.getresponse()
        h.close()
        if response.status / 100 < 4:
            url = url_custom

    if not url:
        youtube_re = re.compile('https?://.*?youtube.com/.*?/([^/?]+)')
        vimeo_re = re.compile('https?://.*?vimeo.com/.*?/([^/?]+)')
        for link in xbmc_common.parseDOM(html, 'iframe', ret='src'):
            match = youtube_re.match(link)
            if match:
                url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % (match.group(1))
                break
            match = vimeo_re.match(link)
            if match:
                url = 'plugin://plugin.video.vimeo?action=play_video&videoid=%s' % (match.group(1))
                break

    # TODO if not url: display error

    return url, title, speaker, plot