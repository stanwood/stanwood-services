# The MIT License (MIT)
# 
# Copyright (c) 2018 stanwood GmbH
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import random

if __name__ == "__main__":

    urls = []
    for x in xrange(10):
        # a_url = "https://image.kurier.at/images/cfs_landscape_616w_308h/3037821/46-115171909.jpg"
        # token = "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnVZVzFsYzNCaFkyVWlPaUp3Y0NKOS5NMVpQTkdSVVlFdnJ1YlhZNVlpYjdfWU5kXzdGWEliOVpHOTJDbmNkWHBr"
        # ccc = '?{}'.format(random.randint(100, 1000))
        a_url = "https://storage.googleapis.com/stanwood-pdf-service.appspot.com/storage.googleapis.com/funke-hq-api.appspot.com/upload/NRZ.DUISBURGNORD.2018-10-31.015.pdf/1.png" #  + ccc
        token = 'ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnVZVzFsYzNCaFkyVWlPaUpyZFhKcFpYSWlmUS5lM2VRQWtEcW1pMEZ1bGNvVGJDRlNJZTlQM0RJSUFJM0czQ0k5VlJmSFBn'

        url = '"http://test-dot-stanwood-image-service.appspot.com/kurier/image?width={}&token={}&url={}"'.format(random.randint(900, 1060), token, a_url)
        urls.append(url)

    print ' '.join(urls)

# http://stanwood-image-service-dev.appspot.com/piotr/image?token=ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnVZVzFsYzNCaFkyVWlPaUp3YVc5MGNpSjkuYmRBTG5JU1JVTnhhSE16UDQ0UjdBUzRSSi05bFJIa0d6c0VFMjBBaTA4MA==&width=1040&url=https://storage.googleapis.com/stanwood-image-service.appspot.com/funkehq/1-61a0b999b7934af2bdc76709985bb116.png